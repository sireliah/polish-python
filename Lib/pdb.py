#! /usr/bin/env python3

"""
The Python Debugger Pdb
=======================

To use the debugger w its simplest form:

        >>> zaimportuj pdb
        >>> pdb.run('<a statement>')

The debugger's prompt jest '(Pdb) '.  This will stop w the first
function call w <a statement>.

Alternatively, jeżeli a statement terminated przy an unhandled exception,
you can use pdb's post-mortem facility to inspect the contents of the
traceback:

        >>> <a statement>
        <exception traceback>
        >>> zaimportuj pdb
        >>> pdb.pm()

The commands recognized by the debugger are listed w the next
section.  Most can be abbreviated jako indicated; e.g., h(elp) means
that 'help' can be typed jako 'h' albo 'help' (but nie jako 'he' albo 'hel',
nor jako 'H' albo 'Help' albo 'HELP').  Optional arguments are enclosed w
square brackets.  Alternatives w the command syntax are separated
by a vertical bar (|).

A blank line repeats the previous command literally, wyjąwszy for
'list', where it lists the next 11 lines.

Commands that the debugger doesn't recognize are assumed to be Python
statements oraz are executed w the context of the program being
debugged.  Python statements can also be prefixed przy an exclamation
point ('!').  This jest a powerful way to inspect the program being
debugged; it jest even possible to change variables albo call functions.
When an exception occurs w such a statement, the exception name jest
printed but the debugger's state jest nie changed.

The debugger supports aliases, which can save typing.  And aliases can
have parameters (see the alias help entry) which allows one a certain
level of adaptability to the context under examination.

Multiple commands may be entered on a single line, separated by the
pair ';;'.  No intelligence jest applied to separating the commands; the
input jest split at the first ';;', even jeżeli it jest w the middle of a
quoted string.

If a file ".pdbrc" exists w your home directory albo w the current
directory, it jest read w oraz executed jako jeżeli it had been typed at the
debugger prompt.  This jest particularly useful dla aliases.  If both
files exist, the one w the home directory jest read first oraz aliases
defined there can be overriden by the local file.

Aside z aliases, the debugger jest nie directly programmable; but it
is implemented jako a klasa z which you can derive your own debugger
class, which you can make jako fancy jako you like.


Debugger commands
=================

"""
# NOTE: the actual command documentation jest collected z docstrings of the
# commands oraz jest appended to __doc__ after the klasa has been defined.

zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj cmd
zaimportuj bdb
zaimportuj dis
zaimportuj code
zaimportuj glob
zaimportuj pprint
zaimportuj signal
zaimportuj inspect
zaimportuj traceback
zaimportuj linecache


klasa Restart(Exception):
    """Causes a debugger to be restarted dla the debugged python program."""
    dalej

__all__ = ["run", "pm", "Pdb", "runeval", "runctx", "runcall", "set_trace",
           "post_mortem", "help"]

def find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % re.escape(funcname))
    spróbuj:
        fp = open(filename)
    wyjąwszy OSError:
        zwróć Nic
    # consumer of this info expects the first line to be 1
    przy fp:
        dla lineno, line w enumerate(fp, start=1):
            jeżeli cre.match(line):
                zwróć funcname, filename, lineno
    zwróć Nic

def getsourcelines(obj):
    lines, lineno = inspect.findsource(obj)
    jeżeli inspect.isframe(obj) oraz obj.f_globals jest obj.f_locals:
        # must be a module frame: do nie try to cut a block out of it
        zwróć lines, 1
    albo_inaczej inspect.ismodule(obj):
        zwróć lines, 1
    zwróć inspect.getblock(lines[lineno:]), lineno+1

def lasti2lineno(code, lasti):
    linestarts = list(dis.findlinestarts(code))
    linestarts.reverse()
    dla i, lineno w linestarts:
        jeżeli lasti >= i:
            zwróć lineno
    zwróć 0


klasa _rstr(str):
    """String that doesn't quote its repr."""
    def __repr__(self):
        zwróć self


# Interaction prompt line will separate file oraz call info z code
# text using value of line_prefix string.  A newline oraz arrow may
# be to your liking.  You can set it once pdb jest imported using the
# command "pdb.line_prefix = '\n% '".
# line_prefix = ': '    # Use this to get the old situation back
line_prefix = '\n-> '   # Probably a better default

klasa Pdb(bdb.Bdb, cmd.Cmd):

    def __init__(self, completekey='tab', stdin=Nic, stdout=Nic, skip=Nic,
                 nosigint=Nieprawda):
        bdb.Bdb.__init__(self, skip=skip)
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        jeżeli stdout:
            self.use_rawinput = 0
        self.prompt = '(Pdb) '
        self.aliases = {}
        self.displaying = {}
        self.mainpyfile = ''
        self._wait_for_mainpyfile = Nieprawda
        self.tb_lineno = {}
        # Try to load readline jeżeli it exists
        spróbuj:
            zaimportuj readline
            # remove some common file name delimiters
            readline.set_completer_delims(' \t\n`@#$%^&*()=+[{]}\\|;:\'",<>?')
        wyjąwszy ImportError:
            dalej
        self.allow_kbdint = Nieprawda
        self.nosigint = nosigint

        # Read $HOME/.pdbrc oraz ./.pdbrc
        self.rcLines = []
        jeżeli 'HOME' w os.environ:
            envHome = os.environ['HOME']
            spróbuj:
                przy open(os.path.join(envHome, ".pdbrc")) jako rcFile:
                    self.rcLines.extend(rcFile)
            wyjąwszy OSError:
                dalej
        spróbuj:
            przy open(".pdbrc") jako rcFile:
                self.rcLines.extend(rcFile)
        wyjąwszy OSError:
            dalej

        self.commands = {} # associates a command list to przerwijpoint numbers
        self.commands_doprompt = {} # dla each bp num, tells jeżeli the prompt
                                    # must be disp. after execing the cmd list
        self.commands_silent = {} # dla each bp num, tells jeżeli the stack trace
                                  # must be disp. after execing the cmd list
        self.commands_defining = Nieprawda # Prawda dopóki w the process of defining
                                       # a command list
        self.commands_bnum = Nic # The przerwijpoint number dla which we are
                                  # defining a list

    def sigint_handler(self, signum, frame):
        jeżeli self.allow_kbdint:
            podnieś KeyboardInterrupt
        self.message("\nProgram interrupted. (Use 'cont' to resume).")
        self.set_step()
        self.set_trace(frame)
        # restore previous signal handler
        signal.signal(signal.SIGINT, self._previous_sigint_handler)

    def reset(self):
        bdb.Bdb.reset(self)
        self.forget()

    def forget(self):
        self.lineno = Nic
        self.stack = []
        self.curindex = 0
        self.curframe = Nic
        self.tb_lineno.clear()

    def setup(self, f, tb):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, tb)
        dopóki tb:
            # when setting up post-mortem debugging przy a traceback, save all
            # the original line numbers to be displayed along the current line
            # numbers (which can be different, e.g. due to finally clauses)
            lineno = lasti2lineno(tb.tb_frame.f_code, tb.tb_lasti)
            self.tb_lineno[tb.tb_frame] = lineno
            tb = tb.tb_next
        self.curframe = self.stack[self.curindex][0]
        # The f_locals dictionary jest updated z the actual frame
        # locals whenever the .f_locals accessor jest called, so we
        # cache it here to ensure that modifications are nie overwritten.
        self.curframe_locals = self.curframe.f_locals
        zwróć self.execRcLines()

    # Can be executed earlier than 'setup' jeżeli desired
    def execRcLines(self):
        jeżeli nie self.rcLines:
            zwróć
        # local copy because of recursion
        rcLines = self.rcLines
        rcLines.reverse()
        # execute every line only once
        self.rcLines = []
        dopóki rcLines:
            line = rcLines.pop().strip()
            jeżeli line oraz line[0] != '#':
                jeżeli self.onecmd(line):
                    # jeżeli onecmd returns Prawda, the command wants to exit
                    # z the interaction, save leftover rc lines
                    # to execute before next interaction
                    self.rcLines += reversed(rcLines)
                    zwróć Prawda

    # Override Bdb methods

    def user_call(self, frame, argument_list):
        """This method jest called when there jest the remote possibility
        that we ever need to stop w this function."""
        jeżeli self._wait_for_mainpyfile:
            zwróć
        jeżeli self.stop_here(frame):
            self.message('--Call--')
            self.interaction(frame, Nic)

    def user_line(self, frame):
        """This function jest called when we stop albo przerwij at this line."""
        jeżeli self._wait_for_mainpyfile:
            jeżeli (self.mainpyfile != self.canonic(frame.f_code.co_filename)
                albo frame.f_lineno <= 0):
                zwróć
            self._wait_for_mainpyfile = Nieprawda
        jeżeli self.bp_commands(frame):
            self.interaction(frame, Nic)

    def bp_commands(self, frame):
        """Call every command that was set dla the current active przerwijpoint
        (jeżeli there jest one).

        Returns Prawda jeżeli the normal interaction function must be called,
        Nieprawda otherwise."""
        # self.currentbp jest set w bdb w Bdb.break_here jeżeli a przerwijpoint was hit
        jeżeli getattr(self, "currentbp", Nieprawda) oraz \
               self.currentbp w self.commands:
            currentbp = self.currentbp
            self.currentbp = 0
            lastcmd_back = self.lastcmd
            self.setup(frame, Nic)
            dla line w self.commands[currentbp]:
                self.onecmd(line)
            self.lastcmd = lastcmd_back
            jeżeli nie self.commands_silent[currentbp]:
                self.print_stack_entry(self.stack[self.curindex])
            jeżeli self.commands_doprompt[currentbp]:
                self._cmdloop()
            self.forget()
            zwróć
        zwróć 1

    def user_return(self, frame, return_value):
        """This function jest called when a zwróć trap jest set here."""
        jeżeli self._wait_for_mainpyfile:
            zwróć
        frame.f_locals['__return__'] = return_value
        self.message('--Return--')
        self.interaction(frame, Nic)

    def user_exception(self, frame, exc_info):
        """This function jest called jeżeli an exception occurs,
        but only jeżeli we are to stop at albo just below this level."""
        jeżeli self._wait_for_mainpyfile:
            zwróć
        exc_type, exc_value, exc_traceback = exc_info
        frame.f_locals['__exception__'] = exc_type, exc_value

        # An 'Internal StopIteration' exception jest an exception debug event
        # issued by the interpreter when handling a subgenerator run with
        # 'uzyskaj from' albo a generator controled by a dla loop. No exception has
        # actually occurred w this case. The debugger uses this debug event to
        # stop when the debuggee jest returning z such generators.
        prefix = 'Internal ' jeżeli (nie exc_traceback
                                    oraz exc_type jest StopIteration) inaczej ''
        self.message('%s%s' % (prefix,
            traceback.format_exception_only(exc_type, exc_value)[-1].strip()))
        self.interaction(frame, exc_traceback)

    # General interaction function
    def _cmdloop(self):
        dopóki Prawda:
            spróbuj:
                # keyboard interrupts allow dla an easy way to cancel
                # the current command, so allow them during interactive input
                self.allow_kbdint = Prawda
                self.cmdloop()
                self.allow_kbdint = Nieprawda
                przerwij
            wyjąwszy KeyboardInterrupt:
                self.message('--KeyboardInterrupt--')

    # Called before loop, handles display expressions
    def preloop(self):
        displaying = self.displaying.get(self.curframe)
        jeżeli displaying:
            dla expr, oldvalue w displaying.items():
                newvalue = self._getval_except(expr)
                # check dla identity first; this prevents custom __eq__ to
                # be called at every loop, oraz also prevents instances whose
                # fields are changed to be displayed
                jeżeli newvalue jest nie oldvalue oraz newvalue != oldvalue:
                    displaying[expr] = newvalue
                    self.message('display %s: %r  [old: %r]' %
                                 (expr, newvalue, oldvalue))

    def interaction(self, frame, traceback):
        jeżeli self.setup(frame, traceback):
            # no interaction desired at this time (happens jeżeli .pdbrc contains
            # a command like "continue")
            self.forget()
            zwróć
        self.print_stack_entry(self.stack[self.curindex])
        self._cmdloop()
        self.forget()

    def displayhook(self, obj):
        """Custom displayhook dla the exec w default(), which prevents
        assignment of the _ variable w the builtins.
        """
        # reproduce the behavior of the standard displayhook, nie printing Nic
        jeżeli obj jest nie Nic:
            self.message(repr(obj))

    def default(self, line):
        jeżeli line[:1] == '!': line = line[1:]
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        spróbuj:
            code = compile(line + '\n', '<stdin>', 'single')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            spróbuj:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                exec(code, globals, locals)
            w_końcu:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        wyjąwszy:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())

    def precmd(self, line):
        """Handle alias expansion oraz ';;' separator."""
        jeżeli nie line.strip():
            zwróć line
        args = line.split()
        dopóki args[0] w self.aliases:
            line = self.aliases[args[0]]
            ii = 1
            dla tmpArg w args[1:]:
                line = line.replace("%" + str(ii),
                                      tmpArg)
                ii += 1
            line = line.replace("%*", ' '.join(args[1:]))
            args = line.split()
        # split into ';;' separated commands
        # unless it's an alias command
        jeżeli args[0] != 'alias':
            marker = line.find(';;')
            jeżeli marker >= 0:
                # queue up everything after marker
                next = line[marker+2:].lstrip()
                self.cmdqueue.append(next)
                line = line[:marker].rstrip()
        zwróć line

    def onecmd(self, line):
        """Interpret the argument jako though it had been typed w response
        to the prompt.

        Checks whether this line jest typed at the normal prompt albo w
        a przerwijpoint command list definition.
        """
        jeżeli nie self.commands_defining:
            zwróć cmd.Cmd.onecmd(self, line)
        inaczej:
            zwróć self.handle_command_def(line)

    def handle_command_def(self, line):
        """Handles one command line during command list definition."""
        cmd, arg, line = self.parseline(line)
        jeżeli nie cmd:
            zwróć
        jeżeli cmd == 'silent':
            self.commands_silent[self.commands_bnum] = Prawda
            zwróć # continue to handle other cmd def w the cmd list
        albo_inaczej cmd == 'end':
            self.cmdqueue = []
            zwróć 1 # end of cmd list
        cmdlist = self.commands[self.commands_bnum]
        jeżeli arg:
            cmdlist.append(cmd+' '+arg)
        inaczej:
            cmdlist.append(cmd)
        # Determine jeżeli we must stop
        spróbuj:
            func = getattr(self, 'do_' + cmd)
        wyjąwszy AttributeError:
            func = self.default
        # one of the resuming commands
        jeżeli func.__name__ w self.commands_resuming:
            self.commands_doprompt[self.commands_bnum] = Nieprawda
            self.cmdqueue = []
            zwróć 1
        zwróć

    # interface abstraction functions

    def message(self, msg):
        print(msg, file=self.stdout)

    def error(self, msg):
        print('***', msg, file=self.stdout)

    # Generic completion functions.  Individual complete_foo methods can be
    # assigned below to one of these functions.

    def _complete_location(self, text, line, begidx, endidx):
        # Complete a file/module/function location dla przerwij/tbreak/clear.
        jeżeli line.strip().endswith((':', ',')):
            # Here comes a line number albo a condition which we can't complete.
            zwróć []
        # First, try to find matching functions (i.e. expressions).
        spróbuj:
            ret = self._complete_expression(text, line, begidx, endidx)
        wyjąwszy Exception:
            ret = []
        # Then, try to complete file names jako well.
        globs = glob.glob(text + '*')
        dla fn w globs:
            jeżeli os.path.isdir(fn):
                ret.append(fn + '/')
            albo_inaczej os.path.isfile(fn) oraz fn.lower().endswith(('.py', '.pyw')):
                ret.append(fn + ':')
        zwróć ret

    def _complete_bpnumber(self, text, line, begidx, endidx):
        # Complete a przerwijpoint number.  (This would be more helpful jeżeli we could
        # display additional info along przy the completions, such jako file/line
        # of the przerwijpoint.)
        zwróć [str(i) dla i, bp w enumerate(bdb.Breakpoint.bpbynumber)
                jeżeli bp jest nie Nic oraz str(i).startswith(text)]

    def _complete_expression(self, text, line, begidx, endidx):
        # Complete an arbitrary expression.
        jeżeli nie self.curframe:
            zwróć []
        # Collect globals oraz locals.  It jest usually nie really sensible to also
        # complete builtins, oraz they clutter the namespace quite heavily, so we
        # leave them out.
        ns = self.curframe.f_globals.copy()
        ns.update(self.curframe_locals)
        jeżeli '.' w text:
            # Walk an attribute chain up to the last part, similar to what
            # rlcompleter does.  This will bail jeżeli any of the parts are nie
            # simple attribute access, which jest what we want.
            dotted = text.split('.')
            spróbuj:
                obj = ns[dotted[0]]
                dla part w dotted[1:-1]:
                    obj = getattr(obj, part)
            wyjąwszy (KeyError, AttributeError):
                zwróć []
            prefix = '.'.join(dotted[:-1]) + '.'
            zwróć [prefix + n dla n w dir(obj) jeżeli n.startswith(dotted[-1])]
        inaczej:
            # Complete a simple name.
            zwróć [n dla n w ns.keys() jeżeli n.startswith(text)]

    # Command definitions, called by cmdloop()
    # The argument jest the remaining string on the command line
    # Return true to exit z the command loop

    def do_commands(self, arg):
        """commands [bpnumber]
        (com) ...
        (com) end
        (Pdb)

        Specify a list of commands dla przerwijpoint number bpnumber.
        The commands themselves are entered on the following lines.
        Type a line containing just 'end' to terminate the commands.
        The commands are executed when the przerwijpoint jest hit.

        To remove all commands z a przerwijpoint, type commands oraz
        follow it immediately przy end; that is, give no commands.

        With no bpnumber argument, commands refers to the last
        przerwijpoint set.

        You can use przerwijpoint commands to start your program up
        again.  Simply use the continue command, albo step, albo any other
        command that resumes execution.

        Specifying any command resuming execution (currently continue,
        step, next, return, jump, quit oraz their abbreviations)
        terminates the command list (as jeżeli that command was
        immediately followed by end).  This jest because any time you
        resume execution (even przy a simple next albo step), you may
        encounter another przerwijpoint -- which could have its own
        command list, leading to ambiguities about which list to
        execute.

        If you use the 'silent' command w the command list, the usual
        message about stopping at a przerwijpoint jest nie printed.  This
        may be desirable dla przerwijpoints that are to print a specific
        message oraz then continue.  If none of the other commands
        print anything, you will see no sign that the przerwijpoint was
        reached.
        """
        jeżeli nie arg:
            bnum = len(bdb.Breakpoint.bpbynumber) - 1
        inaczej:
            spróbuj:
                bnum = int(arg)
            wyjąwszy:
                self.error("Usage: commands [bnum]\n        ...\n        end")
                zwróć
        self.commands_bnum = bnum
        # Save old definitions dla the case of a keyboard interrupt.
        jeżeli bnum w self.commands:
            old_command_defs = (self.commands[bnum],
                                self.commands_doprompt[bnum],
                                self.commands_silent[bnum])
        inaczej:
            old_command_defs = Nic
        self.commands[bnum] = []
        self.commands_doprompt[bnum] = Prawda
        self.commands_silent[bnum] = Nieprawda

        prompt_back = self.prompt
        self.prompt = '(com) '
        self.commands_defining = Prawda
        spróbuj:
            self.cmdloop()
        wyjąwszy KeyboardInterrupt:
            # Restore old definitions.
            jeżeli old_command_defs:
                self.commands[bnum] = old_command_defs[0]
                self.commands_doprompt[bnum] = old_command_defs[1]
                self.commands_silent[bnum] = old_command_defs[2]
            inaczej:
                usuń self.commands[bnum]
                usuń self.commands_doprompt[bnum]
                usuń self.commands_silent[bnum]
            self.error('command definition aborted, old commands restored')
        w_końcu:
            self.commands_defining = Nieprawda
            self.prompt = prompt_back

    complete_commands = _complete_bpnumber

    def do_break(self, arg, temporary = 0):
        """b(reak) [ ([filename:]lineno | function) [, condition] ]
        Without argument, list all przerwijs.

        With a line number argument, set a przerwij at this line w the
        current file.  With a function name, set a przerwij at the first
        executable line of that function.  If a second argument jest
        present, it jest a string specifying an expression which must
        evaluate to true before the przerwijpoint jest honored.

        The line number may be prefixed przy a filename oraz a colon,
        to specify a przerwijpoint w another file (probably one that
        hasn't been loaded yet).  The file jest searched dla on
        sys.path; the .py suffix may be omitted.
        """
        jeżeli nie arg:
            jeżeli self.breaks:  # There's at least one
                self.message("Num Type         Disp Enb   Where")
                dla bp w bdb.Breakpoint.bpbynumber:
                    jeżeli bp:
                        self.message(bp.bpformat())
            zwróć
        # parse arguments; comma has lowest precedence
        # oraz cannot occur w filename
        filename = Nic
        lineno = Nic
        cond = Nic
        comma = arg.find(',')
        jeżeli comma > 0:
            # parse stuff after comma: "condition"
            cond = arg[comma+1:].lstrip()
            arg = arg[:comma].rstrip()
        # parse stuff before comma: [filename:]lineno | function
        colon = arg.rfind(':')
        funcname = Nic
        jeżeli colon >= 0:
            filename = arg[:colon].rstrip()
            f = self.lookupmodule(filename)
            jeżeli nie f:
                self.error('%r nie found z sys.path' % filename)
                zwróć
            inaczej:
                filename = f
            arg = arg[colon+1:].lstrip()
            spróbuj:
                lineno = int(arg)
            wyjąwszy ValueError:
                self.error('Bad lineno: %s' % arg)
                zwróć
        inaczej:
            # no colon; can be lineno albo function
            spróbuj:
                lineno = int(arg)
            wyjąwszy ValueError:
                spróbuj:
                    func = eval(arg,
                                self.curframe.f_globals,
                                self.curframe_locals)
                wyjąwszy:
                    func = arg
                spróbuj:
                    jeżeli hasattr(func, '__func__'):
                        func = func.__func__
                    code = func.__code__
                    #use co_name to identify the bkpt (function names
                    #could be aliased, but co_name jest invariant)
                    funcname = code.co_name
                    lineno = code.co_firstlineno
                    filename = code.co_filename
                wyjąwszy:
                    # last thing to try
                    (ok, filename, ln) = self.lineinfo(arg)
                    jeżeli nie ok:
                        self.error('The specified object %r jest nie a function '
                                   'or was nie found along sys.path.' % arg)
                        zwróć
                    funcname = ok # ok contains a function name
                    lineno = int(ln)
        jeżeli nie filename:
            filename = self.defaultFile()
        # Check dla reasonable przerwijpoint
        line = self.checkline(filename, lineno)
        jeżeli line:
            # now set the przerwij point
            err = self.set_break(filename, line, temporary, cond, funcname)
            jeżeli err:
                self.error(err)
            inaczej:
                bp = self.get_breaks(filename, line)[-1]
                self.message("Breakpoint %d at %s:%d" %
                             (bp.number, bp.file, bp.line))

    # To be overridden w derived debuggers
    def defaultFile(self):
        """Produce a reasonable default."""
        filename = self.curframe.f_code.co_filename
        jeżeli filename == '<string>' oraz self.mainpyfile:
            filename = self.mainpyfile
        zwróć filename

    do_b = do_break

    complete_break = _complete_location
    complete_b = _complete_location

    def do_tbreak(self, arg):
        """tbreak [ ([filename:]lineno | function) [, condition] ]
        Same arguments jako przerwij, but sets a temporary przerwijpoint: it
        jest automatically deleted when first hit.
        """
        self.do_break(arg, 1)

    complete_tbreak = _complete_location

    def lineinfo(self, identifier):
        failed = (Nic, Nic, Nic)
        # Input jest identifier, may be w single quotes
        idstring = identifier.split("'")
        jeżeli len(idstring) == 1:
            # nie w single quotes
            id = idstring[0].strip()
        albo_inaczej len(idstring) == 3:
            # quoted
            id = idstring[1].strip()
        inaczej:
            zwróć failed
        jeżeli id == '': zwróć failed
        parts = id.split('.')
        # Protection dla derived debuggers
        jeżeli parts[0] == 'self':
            usuń parts[0]
            jeżeli len(parts) == 0:
                zwróć failed
        # Best first guess at file to look at
        fname = self.defaultFile()
        jeżeli len(parts) == 1:
            item = parts[0]
        inaczej:
            # More than one part.
            # First jest module, second jest method/class
            f = self.lookupmodule(parts[0])
            jeżeli f:
                fname = f
            item = parts[1]
        answer = find_function(item, fname)
        zwróć answer albo failed

    def checkline(self, filename, lineno):
        """Check whether specified line seems to be executable.

        Return `lineno` jeżeli it is, 0 jeżeli nie (e.g. a docstring, comment, blank
        line albo EOF). Warning: testing jest nie comprehensive.
        """
        # this method should be callable before starting debugging, so default
        # to "no globals" jeżeli there jest no current frame
        globs = self.curframe.f_globals jeżeli hasattr(self, 'curframe') inaczej Nic
        line = linecache.getline(filename, lineno, globs)
        jeżeli nie line:
            self.message('End of file')
            zwróć 0
        line = line.strip()
        # Don't allow setting przerwijpoint at a blank line
        jeżeli (nie line albo (line[0] == '#') albo
             (line[:3] == '"""') albo line[:3] == "'''"):
            self.error('Blank albo comment')
            zwróć 0
        zwróć lineno

    def do_enable(self, arg):
        """enable bpnumber [bpnumber ...]
        Enables the przerwijpoints given jako a space separated list of
        przerwijpoint numbers.
        """
        args = arg.split()
        dla i w args:
            spróbuj:
                bp = self.get_bpbynumber(i)
            wyjąwszy ValueError jako err:
                self.error(err)
            inaczej:
                bp.enable()
                self.message('Enabled %s' % bp)

    complete_enable = _complete_bpnumber

    def do_disable(self, arg):
        """disable bpnumber [bpnumber ...]
        Disables the przerwijpoints given jako a space separated list of
        przerwijpoint numbers.  Disabling a przerwijpoint means it cannot
        cause the program to stop execution, but unlike clearing a
        przerwijpoint, it remains w the list of przerwijpoints oraz can be
        (re-)enabled.
        """
        args = arg.split()
        dla i w args:
            spróbuj:
                bp = self.get_bpbynumber(i)
            wyjąwszy ValueError jako err:
                self.error(err)
            inaczej:
                bp.disable()
                self.message('Disabled %s' % bp)

    complete_disable = _complete_bpnumber

    def do_condition(self, arg):
        """condition bpnumber [condition]
        Set a new condition dla the przerwijpoint, an expression which
        must evaluate to true before the przerwijpoint jest honored.  If
        condition jest absent, any existing condition jest removed; i.e.,
        the przerwijpoint jest made unconditional.
        """
        args = arg.split(' ', 1)
        spróbuj:
            cond = args[1]
        wyjąwszy IndexError:
            cond = Nic
        spróbuj:
            bp = self.get_bpbynumber(args[0].strip())
        wyjąwszy IndexError:
            self.error('Breakpoint number expected')
        wyjąwszy ValueError jako err:
            self.error(err)
        inaczej:
            bp.cond = cond
            jeżeli nie cond:
                self.message('Breakpoint %d jest now unconditional.' % bp.number)
            inaczej:
                self.message('New condition set dla przerwijpoint %d.' % bp.number)

    complete_condition = _complete_bpnumber

    def do_ignore(self, arg):
        """ignore bpnumber [count]
        Set the ignore count dla the given przerwijpoint number.  If
        count jest omitted, the ignore count jest set to 0.  A przerwijpoint
        becomes active when the ignore count jest zero.  When non-zero,
        the count jest decremented each time the przerwijpoint jest reached
        oraz the przerwijpoint jest nie disabled oraz any associated
        condition evaluates to true.
        """
        args = arg.split()
        spróbuj:
            count = int(args[1].strip())
        wyjąwszy:
            count = 0
        spróbuj:
            bp = self.get_bpbynumber(args[0].strip())
        wyjąwszy IndexError:
            self.error('Breakpoint number expected')
        wyjąwszy ValueError jako err:
            self.error(err)
        inaczej:
            bp.ignore = count
            jeżeli count > 0:
                jeżeli count > 1:
                    countstr = '%d crossings' % count
                inaczej:
                    countstr = '1 crossing'
                self.message('Will ignore next %s of przerwijpoint %d.' %
                             (countstr, bp.number))
            inaczej:
                self.message('Will stop next time przerwijpoint %d jest reached.'
                             % bp.number)

    complete_ignore = _complete_bpnumber

    def do_clear(self, arg):
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of przerwijpoint numbers, clear
        those przerwijpoints.  Without argument, clear all przerwijs (but
        first ask confirmation).  With a filename:lineno argument,
        clear all przerwijs at that line w that file.
        """
        jeżeli nie arg:
            spróbuj:
                reply = input('Clear all przerwijs? ')
            wyjąwszy EOFError:
                reply = 'no'
            reply = reply.strip().lower()
            jeżeli reply w ('y', 'yes'):
                bplist = [bp dla bp w bdb.Breakpoint.bpbynumber jeżeli bp]
                self.clear_all_breaks()
                dla bp w bplist:
                    self.message('Deleted %s' % bp)
            zwróć
        jeżeli ':' w arg:
            # Make sure it works dla "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i+1:]
            spróbuj:
                lineno = int(arg)
            wyjąwszy ValueError:
                err = "Invalid line number (%s)" % arg
            inaczej:
                bplist = self.get_breaks(filename, lineno)
                err = self.clear_break(filename, lineno)
            jeżeli err:
                self.error(err)
            inaczej:
                dla bp w bplist:
                    self.message('Deleted %s' % bp)
            zwróć
        numberlist = arg.split()
        dla i w numberlist:
            spróbuj:
                bp = self.get_bpbynumber(i)
            wyjąwszy ValueError jako err:
                self.error(err)
            inaczej:
                self.clear_bpbynumber(i)
                self.message('Deleted %s' % bp)
    do_cl = do_clear # 'c' jest already an abbreviation dla 'continue'

    complete_clear = _complete_location
    complete_cl = _complete_location

    def do_where(self, arg):
        """w(here)
        Print a stack trace, przy the most recent frame at the bottom.
        An arrow indicates the "current frame", which determines the
        context of most commands.  'bt' jest an alias dla this command.
        """
        self.print_stack_trace()
    do_w = do_where
    do_bt = do_where

    def _select_frame(self, number):
        assert 0 <= number < len(self.stack)
        self.curindex = number
        self.curframe = self.stack[self.curindex][0]
        self.curframe_locals = self.curframe.f_locals
        self.print_stack_entry(self.stack[self.curindex])
        self.lineno = Nic

    def do_up(self, arg):
        """u(p) [count]
        Move the current frame count (default one) levels up w the
        stack trace (to an older frame).
        """
        jeżeli self.curindex == 0:
            self.error('Oldest frame')
            zwróć
        spróbuj:
            count = int(arg albo 1)
        wyjąwszy ValueError:
            self.error('Invalid frame count (%s)' % arg)
            zwróć
        jeżeli count < 0:
            newframe = 0
        inaczej:
            newframe = max(0, self.curindex - count)
        self._select_frame(newframe)
    do_u = do_up

    def do_down(self, arg):
        """d(own) [count]
        Move the current frame count (default one) levels down w the
        stack trace (to a newer frame).
        """
        jeżeli self.curindex + 1 == len(self.stack):
            self.error('Newest frame')
            zwróć
        spróbuj:
            count = int(arg albo 1)
        wyjąwszy ValueError:
            self.error('Invalid frame count (%s)' % arg)
            zwróć
        jeżeli count < 0:
            newframe = len(self.stack) - 1
        inaczej:
            newframe = min(len(self.stack) - 1, self.curindex + count)
        self._select_frame(newframe)
    do_d = do_down

    def do_until(self, arg):
        """unt(il) [lineno]
        Without argument, continue execution until the line przy a
        number greater than the current one jest reached.  With a line
        number, continue execution until a line przy a number greater
        albo equal to that jest reached.  In both cases, also stop when
        the current frame returns.
        """
        jeżeli arg:
            spróbuj:
                lineno = int(arg)
            wyjąwszy ValueError:
                self.error('Error w argument: %r' % arg)
                zwróć
            jeżeli lineno <= self.curframe.f_lineno:
                self.error('"until" line number jest smaller than current '
                           'line number')
                zwróć
        inaczej:
            lineno = Nic
        self.set_until(self.curframe, lineno)
        zwróć 1
    do_unt = do_until

    def do_step(self, arg):
        """s(tep)
        Execute the current line, stop at the first possible occasion
        (either w a function that jest called albo w the current
        function).
        """
        self.set_step()
        zwróć 1
    do_s = do_step

    def do_next(self, arg):
        """n(ext)
        Continue execution until the next line w the current function
        jest reached albo it returns.
        """
        self.set_next(self.curframe)
        zwróć 1
    do_n = do_next

    def do_run(self, arg):
        """run [args...]
        Restart the debugged python program. If a string jest supplied
        it jest split przy "shlex", oraz the result jest used jako the new
        sys.argv.  History, przerwijpoints, actions oraz debugger options
        are preserved.  "restart" jest an alias dla "run".
        """
        jeżeli arg:
            zaimportuj shlex
            argv0 = sys.argv[0:1]
            sys.argv = shlex.split(arg)
            sys.argv[:0] = argv0
        # this jest caught w the main debugger loop
        podnieś Restart

    do_restart = do_run

    def do_return(self, arg):
        """r(eturn)
        Continue execution until the current function returns.
        """
        self.set_return(self.curframe)
        zwróć 1
    do_r = do_zwróć

    def do_continue(self, arg):
        """c(ont(inue))
        Continue execution, only stop when a przerwijpoint jest encountered.
        """
        jeżeli nie self.nosigint:
            spróbuj:
                self._previous_sigint_handler = \
                    signal.signal(signal.SIGINT, self.sigint_handler)
            wyjąwszy ValueError:
                # ValueError happens when do_continue() jest invoked from
                # a non-main thread w which case we just continue without
                # SIGINT set. Would printing a message here (once) make
                # sense?
                dalej
        self.set_continue()
        zwróć 1
    do_c = do_cont = do_kontynuuj

    def do_jump(self, arg):
        """j(ump) lineno
        Set the next line that will be executed.  Only available w
        the bottom-most frame.  This lets you jump back oraz execute
        code again, albo jump forward to skip code that you don't want
        to run.

        It should be noted that nie all jumps are allowed -- for
        instance it jest nie possible to jump into the middle of a
        dla loop albo out of a finally clause.
        """
        jeżeli self.curindex + 1 != len(self.stack):
            self.error('You can only jump within the bottom frame')
            zwróć
        spróbuj:
            arg = int(arg)
        wyjąwszy ValueError:
            self.error("The 'jump' command requires a line number")
        inaczej:
            spróbuj:
                # Do the jump, fix up our copy of the stack, oraz display the
                # new position
                self.curframe.f_lineno = arg
                self.stack[self.curindex] = self.stack[self.curindex][0], arg
                self.print_stack_entry(self.stack[self.curindex])
            wyjąwszy ValueError jako e:
                self.error('Jump failed: %s' % e)
    do_j = do_jump

    def do_debug(self, arg):
        """debug code
        Enter a recursive debugger that steps through the code
        argument (which jest an arbitrary expression albo statement to be
        executed w the current environment).
        """
        sys.settrace(Nic)
        globals = self.curframe.f_globals
        locals = self.curframe_locals
        p = Pdb(self.completekey, self.stdin, self.stdout)
        p.prompt = "(%s) " % self.prompt.strip()
        self.message("ENTERING RECURSIVE DEBUGGER")
        sys.call_tracing(p.run, (arg, globals, locals))
        self.message("LEAVING RECURSIVE DEBUGGER")
        sys.settrace(self.trace_dispatch)
        self.lastcmd = p.lastcmd

    complete_debug = _complete_expression

    def do_quit(self, arg):
        """q(uit)\nexit
        Quit z the debugger. The program being executed jest aborted.
        """
        self._user_requested_quit = Prawda
        self.set_quit()
        zwróć 1

    do_q = do_quit
    do_exit = do_quit

    def do_EOF(self, arg):
        """EOF
        Handles the receipt of EOF jako a command.
        """
        self.message('')
        self._user_requested_quit = Prawda
        self.set_quit()
        zwróć 1

    def do_args(self, arg):
        """a(rgs)
        Print the argument list of the current function.
        """
        co = self.curframe.f_code
        dict = self.curframe_locals
        n = co.co_argcount
        jeżeli co.co_flags & 4: n = n+1
        jeżeli co.co_flags & 8: n = n+1
        dla i w range(n):
            name = co.co_varnames[i]
            jeżeli name w dict:
                self.message('%s = %r' % (name, dict[name]))
            inaczej:
                self.message('%s = *** undefined ***' % (name,))
    do_a = do_args

    def do_retval(self, arg):
        """retval
        Print the zwróć value dla the last zwróć of a function.
        """
        jeżeli '__return__' w self.curframe_locals:
            self.message(repr(self.curframe_locals['__return__']))
        inaczej:
            self.error('Not yet returned!')
    do_rv = do_retval

    def _getval(self, arg):
        spróbuj:
            zwróć eval(arg, self.curframe.f_globals, self.curframe_locals)
        wyjąwszy:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())
            podnieś

    def _getval_except(self, arg, frame=Nic):
        spróbuj:
            jeżeli frame jest Nic:
                zwróć eval(arg, self.curframe.f_globals, self.curframe_locals)
            inaczej:
                zwróć eval(arg, frame.f_globals, frame.f_locals)
        wyjąwszy:
            exc_info = sys.exc_info()[:2]
            err = traceback.format_exception_only(*exc_info)[-1].strip()
            zwróć _rstr('** podnieśd %s **' % err)

    def do_p(self, arg):
        """p expression
        Print the value of the expression.
        """
        spróbuj:
            self.message(repr(self._getval(arg)))
        wyjąwszy:
            dalej

    def do_pp(self, arg):
        """pp expression
        Pretty-print the value of the expression.
        """
        spróbuj:
            self.message(pprint.pformat(self._getval(arg)))
        wyjąwszy:
            dalej

    complete_print = _complete_expression
    complete_p = _complete_expression
    complete_pp = _complete_expression

    def do_list(self, arg):
        """l(ist) [first [,last] | .]

        List source code dla the current file.  Without arguments,
        list 11 lines around the current line albo continue the previous
        listing.  With . jako argument, list 11 lines around the current
        line.  With one argument, list 11 lines starting at that line.
        With two arguments, list the given range; jeżeli the second
        argument jest less than the first, it jest a count.

        The current line w the current frame jest indicated by "->".
        If an exception jest being debugged, the line where the
        exception was originally podnieśd albo propagated jest indicated by
        ">>", jeżeli it differs z the current line.
        """
        self.lastcmd = 'list'
        last = Nic
        jeżeli arg oraz arg != '.':
            spróbuj:
                jeżeli ',' w arg:
                    first, last = arg.split(',')
                    first = int(first.strip())
                    last = int(last.strip())
                    jeżeli last < first:
                        # assume it's a count
                        last = first + last
                inaczej:
                    first = int(arg.strip())
                    first = max(1, first - 5)
            wyjąwszy ValueError:
                self.error('Error w argument: %r' % arg)
                zwróć
        albo_inaczej self.lineno jest Nic albo arg == '.':
            first = max(1, self.curframe.f_lineno - 5)
        inaczej:
            first = self.lineno + 1
        jeżeli last jest Nic:
            last = first + 10
        filename = self.curframe.f_code.co_filename
        przerwijlist = self.get_file_breaks(filename)
        spróbuj:
            lines = linecache.getlines(filename, self.curframe.f_globals)
            self._print_lines(lines[first-1:last], first, przerwijlist,
                              self.curframe)
            self.lineno = min(last, len(lines))
            jeżeli len(lines) < last:
                self.message('[EOF]')
        wyjąwszy KeyboardInterrupt:
            dalej
    do_l = do_list

    def do_longlist(self, arg):
        """longlist | ll
        List the whole source code dla the current function albo frame.
        """
        filename = self.curframe.f_code.co_filename
        przerwijlist = self.get_file_breaks(filename)
        spróbuj:
            lines, lineno = getsourcelines(self.curframe)
        wyjąwszy OSError jako err:
            self.error(err)
            zwróć
        self._print_lines(lines, lineno, przerwijlist, self.curframe)
    do_ll = do_longlist

    def do_source(self, arg):
        """source expression
        Try to get source code dla the given object oraz display it.
        """
        spróbuj:
            obj = self._getval(arg)
        wyjąwszy:
            zwróć
        spróbuj:
            lines, lineno = getsourcelines(obj)
        wyjąwszy (OSError, TypeError) jako err:
            self.error(err)
            zwróć
        self._print_lines(lines, lineno)

    complete_source = _complete_expression

    def _print_lines(self, lines, start, przerwijs=(), frame=Nic):
        """Print a range of lines."""
        jeżeli frame:
            current_lineno = frame.f_lineno
            exc_lineno = self.tb_lineno.get(frame, -1)
        inaczej:
            current_lineno = exc_lineno = -1
        dla lineno, line w enumerate(lines, start):
            s = str(lineno).rjust(3)
            jeżeli len(s) < 4:
                s += ' '
            jeżeli lineno w przerwijs:
                s += 'B'
            inaczej:
                s += ' '
            jeżeli lineno == current_lineno:
                s += '->'
            albo_inaczej lineno == exc_lineno:
                s += '>>'
            self.message(s + '\t' + line.rstrip())

    def do_whatis(self, arg):
        """whatis arg
        Print the type of the argument.
        """
        spróbuj:
            value = self._getval(arg)
        wyjąwszy:
            # _getval() already printed the error
            zwróć
        code = Nic
        # Is it a function?
        spróbuj:
            code = value.__code__
        wyjąwszy Exception:
            dalej
        jeżeli code:
            self.message('Function %s' % code.co_name)
            zwróć
        # Is it an instance method?
        spróbuj:
            code = value.__func__.__code__
        wyjąwszy Exception:
            dalej
        jeżeli code:
            self.message('Method %s' % code.co_name)
            zwróć
        # Is it a class?
        jeżeli value.__class__ jest type:
            self.message('Class %s.%s' % (value.__module__, value.__qualname__))
            zwróć
        # Nic of the above...
        self.message(type(value))

    complete_whatis = _complete_expression

    def do_display(self, arg):
        """display [expression]

        Display the value of the expression jeżeli it changed, each time execution
        stops w the current frame.

        Without expression, list all display expressions dla the current frame.
        """
        jeżeli nie arg:
            self.message('Currently displaying:')
            dla item w self.displaying.get(self.curframe, {}).items():
                self.message('%s: %r' % item)
        inaczej:
            val = self._getval_except(arg)
            self.displaying.setdefault(self.curframe, {})[arg] = val
            self.message('display %s: %r' % (arg, val))

    complete_display = _complete_expression

    def do_undisplay(self, arg):
        """undisplay [expression]

        Do nie display the expression any more w the current frame.

        Without expression, clear all display expressions dla the current frame.
        """
        jeżeli arg:
            spróbuj:
                usuń self.displaying.get(self.curframe, {})[arg]
            wyjąwszy KeyError:
                self.error('not displaying %s' % arg)
        inaczej:
            self.displaying.pop(self.curframe, Nic)

    def complete_undisplay(self, text, line, begidx, endidx):
        zwróć [e dla e w self.displaying.get(self.curframe, {})
                jeżeli e.startswith(text)]

    def do_interact(self, arg):
        """interact

        Start an interactive interpreter whose global namespace
        contains all the (global oraz local) names found w the current scope.
        """
        ns = self.curframe.f_globals.copy()
        ns.update(self.curframe_locals)
        code.interact("*interactive*", local=ns)

    def do_alias(self, arg):
        """alias [name [command [parameter parameter ...] ]]
        Create an alias called 'name' that executes 'command'.  The
        command must *not* be enclosed w quotes.  Replaceable
        parameters can be indicated by %1, %2, oraz so on, dopóki %* jest
        replaced by all the parameters.  If no command jest given, the
        current alias dla name jest shown. If no name jest given, all
        aliases are listed.

        Aliases may be nested oraz can contain anything that can be
        legally typed at the pdb prompt.  Note!  You *can* override
        internal pdb commands przy aliases!  Those internal commands
        are then hidden until the alias jest removed.  Aliasing jest
        recursively applied to the first word of the command line; all
        other words w the line are left alone.

        As an example, here are two useful aliases (especially when
        placed w the .pdbrc file):

        # Print instance variables (usage "pi classInst")
        alias pi dla k w %1.__dict__.keys(): print("%1.",k,"=",%1.__dict__[k])
        # Print instance variables w self
        alias ps pi self
        """
        args = arg.split()
        jeżeli len(args) == 0:
            keys = sorted(self.aliases.keys())
            dla alias w keys:
                self.message("%s = %s" % (alias, self.aliases[alias]))
            zwróć
        jeżeli args[0] w self.aliases oraz len(args) == 1:
            self.message("%s = %s" % (args[0], self.aliases[args[0]]))
        inaczej:
            self.aliases[args[0]] = ' '.join(args[1:])

    def do_unalias(self, arg):
        """unalias name
        Delete the specified alias.
        """
        args = arg.split()
        jeżeli len(args) == 0: zwróć
        jeżeli args[0] w self.aliases:
            usuń self.aliases[args[0]]

    def complete_unalias(self, text, line, begidx, endidx):
        zwróć [a dla a w self.aliases jeżeli a.startswith(text)]

    # List of all the commands making the program resume execution.
    commands_resuming = ['do_continue', 'do_step', 'do_next', 'do_return',
                         'do_quit', 'do_jump']

    # Print a traceback starting at the top stack frame.
    # The most recently entered frame jest printed last;
    # this jest different z dbx oraz gdb, but consistent with
    # the Python interpreter's stack trace.
    # It jest also consistent przy the up/down commands (which are
    # compatible przy dbx oraz gdb: up moves towards 'main()'
    # oraz down moves towards the most recent stack frame).

    def print_stack_trace(self):
        spróbuj:
            dla frame_lineno w self.stack:
                self.print_stack_entry(frame_lineno)
        wyjąwszy KeyboardInterrupt:
            dalej

    def print_stack_entry(self, frame_lineno, prompt_prefix=line_prefix):
        frame, lineno = frame_lineno
        jeżeli frame jest self.curframe:
            prefix = '> '
        inaczej:
            prefix = '  '
        self.message(prefix +
                     self.format_stack_entry(frame_lineno, prompt_prefix))

    # Provide help

    def do_help(self, arg):
        """h(elp)
        Without argument, print the list of available commands.
        With a command name jako argument, print help about that command.
        "help pdb" shows the full pdb documentation.
        "help exec" gives help on the ! command.
        """
        jeżeli nie arg:
            zwróć cmd.Cmd.do_help(self, arg)
        spróbuj:
            spróbuj:
                topic = getattr(self, 'help_' + arg)
                zwróć topic()
            wyjąwszy AttributeError:
                command = getattr(self, 'do_' + arg)
        wyjąwszy AttributeError:
            self.error('No help dla %r' % arg)
        inaczej:
            jeżeli sys.flags.optimize >= 2:
                self.error('No help dla %r; please do nie run Python przy -OO '
                           'jeżeli you need command help' % arg)
                zwróć
            self.message(command.__doc__.rstrip())

    do_h = do_help

    def help_exec(self):
        """(!) statement
        Execute the (one-line) statement w the context of the current
        stack frame.  The exclamation point can be omitted unless the
        first word of the statement resembles a debugger command.  To
        assign to a global variable you must always prefix the command
        przy a 'global' command, e.g.:
        (Pdb) global list_options; list_options = ['-l']
        (Pdb)
        """
        self.message((self.help_exec.__doc__ albo '').strip())

    def help_pdb(self):
        help()

    # other helper functions

    def lookupmodule(self, filename):
        """Helper function dla przerwij/clear parsing -- may be overridden.

        lookupmodule() translates (possibly incomplete) file albo module name
        into an absolute file name.
        """
        jeżeli os.path.isabs(filename) oraz  os.path.exists(filename):
            zwróć filename
        f = os.path.join(sys.path[0], filename)
        jeżeli  os.path.exists(f) oraz self.canonic(f) == self.mainpyfile:
            zwróć f
        root, ext = os.path.splitext(filename)
        jeżeli ext == '':
            filename = filename + '.py'
        jeżeli os.path.isabs(filename):
            zwróć filename
        dla dirname w sys.path:
            dopóki os.path.islink(dirname):
                dirname = os.readlink(dirname)
            fullname = os.path.join(dirname, filename)
            jeżeli os.path.exists(fullname):
                zwróć fullname
        zwróć Nic

    def _runscript(self, filename):
        # The script has to run w __main__ namespace (or imports from
        # __main__ will przerwij).
        #
        # So we clear up the __main__ oraz set several special variables
        # (this gets rid of pdb's globals oraz cleans old variables on restarts).
        zaimportuj __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
                                  "__file__"    : filename,
                                  "__builtins__": __builtins__,
                                 })

        # When bdb sets tracing, a number of call oraz line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line oraz
        # user_call dla details).
        self._wait_for_mainpyfile = Prawda
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = Nieprawda
        przy open(filename, "rb") jako fp:
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)

# Collect all command help into docstring, jeżeli nie run przy -OO

jeżeli __doc__ jest nie Nic:
    # unfortunately we can't guess this order z the klasa definition
    _help_order = [
        'help', 'where', 'down', 'up', 'break', 'tbreak', 'clear', 'disable',
        'enable', 'ignore', 'condition', 'commands', 'step', 'next', 'until',
        'jump', 'return', 'retval', 'run', 'continue', 'list', 'longlist',
        'args', 'p', 'pp', 'whatis', 'source', 'display', 'undisplay',
        'interact', 'alias', 'unalias', 'debug', 'quit',
    ]

    dla _command w _help_order:
        __doc__ += getattr(Pdb, 'do_' + _command).__doc__.strip() + '\n\n'
    __doc__ += Pdb.help_exec.__doc__

    usuń _help_order, _command


# Simplified interface

def run(statement, globals=Nic, locals=Nic):
    Pdb().run(statement, globals, locals)

def runeval(expression, globals=Nic, locals=Nic):
    zwróć Pdb().runeval(expression, globals, locals)

def runctx(statement, globals, locals):
    # B/W compatibility
    run(statement, globals, locals)

def runcall(*args, **kwds):
    zwróć Pdb().runcall(*args, **kwds)

def set_trace():
    Pdb().set_trace(sys._getframe().f_back)

# Post-Mortem interface

def post_mortem(t=Nic):
    # handling the default
    jeżeli t jest Nic:
        # sys.exc_info() returns (type, value, traceback) jeżeli an exception jest
        # being handled, otherwise it returns Nic
        t = sys.exc_info()[2]
    jeżeli t jest Nic:
        podnieś ValueError("A valid traceback must be dalejed jeżeli no "
                         "exception jest being handled")

    p = Pdb()
    p.reset()
    p.interaction(Nic, t)

def pm():
    post_mortem(sys.last_traceback)


# Main program dla testing

TESTCMD = 'zaimportuj x; x.main()'

def test():
    run(TESTCMD)

# print help
def help():
    zaimportuj pydoc
    pydoc.pager(__doc__)

_usage = """\
usage: pdb.py [-c command] ... pyfile [arg] ...

Debug the Python program given by pyfile.

Initial commands are read z .pdbrc files w your home directory
and w the current directory, jeżeli they exist.  Commands supplied with
-c are executed after commands z .pdbrc files.

To let the script run until an exception occurs, use "-c continue".
To let the script run up to a given line X w the debugged file, use
"-c 'until X'"."""

def main():
    zaimportuj getopt

    opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['--help', '--command='])

    jeżeli nie args:
        print(_usage)
        sys.exit(2)

    commands = []
    dla opt, optarg w opts:
        jeżeli opt w ['-h', '--help']:
            print(_usage)
            sys.exit()
        albo_inaczej opt w ['-c', '--command']:
            commands.append(optarg)

    mainpyfile = args[0]     # Get script filename
    jeżeli nie os.path.exists(mainpyfile):
        print('Error:', mainpyfile, 'does nie exist')
        sys.exit(1)

    sys.argv[:] = args      # Hide "pdb.py" oraz pdb options z argument list

    # Replace pdb's dir przy script's dir w front of module search path.
    sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user z the command line. There jest a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = Pdb()
    pdb.rcLines.extend(commands)
    dopóki Prawda:
        spróbuj:
            pdb._runscript(mainpyfile)
            jeżeli pdb._user_requested_quit:
                przerwij
            print("The program finished oraz will be restarted")
        wyjąwszy Restart:
            print("Restarting", mainpyfile, "przy arguments:")
            print("\t" + " ".join(args))
        wyjąwszy SystemExit:
            # In most cases SystemExit does nie warrant a post-mortem session.
            print("The program exited via sys.exit(). Exit status:", end=' ')
            print(sys.exc_info()[1])
        wyjąwszy:
            traceback.print_exc()
            print("Uncaught exception. Entering post mortem debugging")
            print("Running 'cont' albo 'step' will restart the program")
            t = sys.exc_info()[2]
            pdb.interaction(Nic, t)
            print("Post mortem debugger finished. The " + mainpyfile +
                  " will be restarted")


# When invoked jako main program, invoke the debugger on a script
jeżeli __name__ == '__main__':
    zaimportuj pdb
    pdb.main()
