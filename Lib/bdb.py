"""Debugger basics"""

zaimportuj fnmatch
zaimportuj sys
zaimportuj os
z inspect zaimportuj CO_GENERATOR

__all__ = ["BdbQuit", "Bdb", "Breakpoint"]

klasa BdbQuit(Exception):
    """Exception to give up completely."""


klasa Bdb:
    """Generic Python debugger base class.

    This klasa takes care of details of the trace facility;
    a derived klasa should implement user interaction.
    The standard debugger klasa (pdb.Pdb) jest an example.
    """

    def __init__(self, skip=Nic):
        self.skip = set(skip) jeżeli skip inaczej Nic
        self.breaks = {}
        self.fncache = {}
        self.frame_returning = Nic

    def canonic(self, filename):
        jeżeli filename == "<" + filename[1:-1] + ">":
            zwróć filename
        canonic = self.fncache.get(filename)
        jeżeli nie canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normcase(canonic)
            self.fncache[filename] = canonic
        zwróć canonic

    def reset(self):
        zaimportuj linecache
        linecache.checkcache()
        self.botframe = Nic
        self._set_stopinfo(Nic, Nic)

    def trace_dispatch(self, frame, event, arg):
        jeżeli self.quitting:
            zwróć # Nic
        jeżeli event == 'line':
            zwróć self.dispatch_line(frame)
        jeżeli event == 'call':
            zwróć self.dispatch_call(frame, arg)
        jeżeli event == 'return':
            zwróć self.dispatch_return(frame, arg)
        jeżeli event == 'exception':
            zwróć self.dispatch_exception(frame, arg)
        jeżeli event == 'c_call':
            zwróć self.trace_dispatch
        jeżeli event == 'c_exception':
            zwróć self.trace_dispatch
        jeżeli event == 'c_return':
            zwróć self.trace_dispatch
        print('bdb.Bdb.dispatch: unknown debugging event:', repr(event))
        zwróć self.trace_dispatch

    def dispatch_line(self, frame):
        jeżeli self.stop_here(frame) albo self.break_here(frame):
            self.user_line(frame)
            jeżeli self.quitting: podnieś BdbQuit
        zwróć self.trace_dispatch

    def dispatch_call(self, frame, arg):
        # XXX 'arg' jest no longer used
        jeżeli self.botframe jest Nic:
            # First call of dispatch since reset()
            self.botframe = frame.f_back # (CT) Note that this may also be Nic!
            zwróć self.trace_dispatch
        jeżeli nie (self.stop_here(frame) albo self.break_anywhere(frame)):
            # No need to trace this function
            zwróć # Nic
        # Ignore call events w generator wyjąwszy when stepping.
        jeżeli self.stopframe oraz frame.f_code.co_flags & CO_GENERATOR:
            zwróć self.trace_dispatch
        self.user_call(frame, arg)
        jeżeli self.quitting: podnieś BdbQuit
        zwróć self.trace_dispatch

    def dispatch_return(self, frame, arg):
        jeżeli self.stop_here(frame) albo frame == self.returnframe:
            # Ignore zwróć events w generator wyjąwszy when stepping.
            jeżeli self.stopframe oraz frame.f_code.co_flags & CO_GENERATOR:
                zwróć self.trace_dispatch
            spróbuj:
                self.frame_returning = frame
                self.user_return(frame, arg)
            w_końcu:
                self.frame_returning = Nic
            jeżeli self.quitting: podnieś BdbQuit
            # The user issued a 'next' albo 'until' command.
            jeżeli self.stopframe jest frame oraz self.stoplineno != -1:
                self._set_stopinfo(Nic, Nic)
        zwróć self.trace_dispatch

    def dispatch_exception(self, frame, arg):
        jeżeli self.stop_here(frame):
            # When stepping przy next/until/return w a generator frame, skip
            # the internal StopIteration exception (przy no traceback)
            # triggered by a subiterator run przy the 'uzyskaj from' statement.
            jeżeli nie (frame.f_code.co_flags & CO_GENERATOR
                    oraz arg[0] jest StopIteration oraz arg[2] jest Nic):
                self.user_exception(frame, arg)
                jeżeli self.quitting: podnieś BdbQuit
        # Stop at the StopIteration albo GeneratorExit exception when the user
        # has set stopframe w a generator by issuing a zwróć command, albo a
        # next/until command at the last statement w the generator before the
        # exception.
        albo_inaczej (self.stopframe oraz frame jest nie self.stopframe
                oraz self.stopframe.f_code.co_flags & CO_GENERATOR
                oraz arg[0] w (StopIteration, GeneratorExit)):
            self.user_exception(frame, arg)
            jeżeli self.quitting: podnieś BdbQuit

        zwróć self.trace_dispatch

    # Normally derived classes don't override the following
    # methods, but they may jeżeli they want to redefine the
    # definition of stopping oraz przerwijpoints.

    def is_skipped_module(self, module_name):
        dla pattern w self.skip:
            jeżeli fnmatch.fnmatch(module_name, pattern):
                zwróć Prawda
        zwróć Nieprawda

    def stop_here(self, frame):
        # (CT) stopframe may now also be Nic, see dispatch_call.
        # (CT) the former test dla Nic jest therefore removed z here.
        jeżeli self.skip oraz \
               self.is_skipped_module(frame.f_globals.get('__name__')):
            zwróć Nieprawda
        jeżeli frame jest self.stopframe:
            jeżeli self.stoplineno == -1:
                zwróć Nieprawda
            zwróć frame.f_lineno >= self.stoplineno
        jeżeli nie self.stopframe:
            zwróć Prawda
        zwróć Nieprawda

    def przerwij_here(self, frame):
        filename = self.canonic(frame.f_code.co_filename)
        jeżeli filename nie w self.breaks:
            zwróć Nieprawda
        lineno = frame.f_lineno
        jeżeli lineno nie w self.breaks[filename]:
            # The line itself has no przerwijpoint, but maybe the line jest the
            # first line of a function przy przerwijpoint set by function name.
            lineno = frame.f_code.co_firstlineno
            jeżeli lineno nie w self.breaks[filename]:
                zwróć Nieprawda

        # flag says ok to delete temp. bp
        (bp, flag) = effective(filename, lineno, frame)
        jeżeli bp:
            self.currentbp = bp.number
            jeżeli (flag oraz bp.temporary):
                self.do_clear(str(bp.number))
            zwróć Prawda
        inaczej:
            zwróć Nieprawda

    def do_clear(self, arg):
        podnieś NotImplementedError("subclass of bdb must implement do_clear()")

    def przerwij_anywhere(self, frame):
        zwróć self.canonic(frame.f_code.co_filename) w self.breaks

    # Derived classes should override the user_* methods
    # to gain control.

    def user_call(self, frame, argument_list):
        """This method jest called when there jest the remote possibility
        that we ever need to stop w this function."""
        dalej

    def user_line(self, frame):
        """This method jest called when we stop albo przerwij at this line."""
        dalej

    def user_return(self, frame, return_value):
        """This method jest called when a zwróć trap jest set here."""
        dalej

    def user_exception(self, frame, exc_info):
        """This method jest called jeżeli an exception occurs,
        but only jeżeli we are to stop at albo just below this level."""
        dalej

    def _set_stopinfo(self, stopframe, returnframe, stoplineno=0):
        self.stopframe = stopframe
        self.returnframe = returnframe
        self.quitting = Nieprawda
        # stoplineno >= 0 means: stop at line >= the stoplineno
        # stoplineno -1 means: don't stop at all
        self.stoplineno = stoplineno

    # Derived classes oraz clients can call the following methods
    # to affect the stepping state.

    def set_until(self, frame, lineno=Nic):
        """Stop when the line przy the line no greater than the current one jest
        reached albo when returning z current frame"""
        # the name "until" jest borrowed z gdb
        jeżeli lineno jest Nic:
            lineno = frame.f_lineno + 1
        self._set_stopinfo(frame, frame, lineno)

    def set_step(self):
        """Stop after one line of code."""
        # Issue #13183: pdb skips frames after hitting a przerwijpoint oraz running
        # step commands.
        # Restore the trace function w the caller (that may nie have been set
        # dla performance reasons) when returning z the current frame.
        jeżeli self.frame_returning:
            caller_frame = self.frame_returning.f_back
            jeżeli caller_frame oraz nie caller_frame.f_trace:
                caller_frame.f_trace = self.trace_dispatch
        self._set_stopinfo(Nic, Nic)

    def set_next(self, frame):
        """Stop on the next line w albo below the given frame."""
        self._set_stopinfo(frame, Nic)

    def set_return(self, frame):
        """Stop when returning z the given frame."""
        jeżeli frame.f_code.co_flags & CO_GENERATOR:
            self._set_stopinfo(frame, Nic, -1)
        inaczej:
            self._set_stopinfo(frame.f_back, frame)

    def set_trace(self, frame=Nic):
        """Start debugging z `frame`.

        If frame jest nie specified, debugging starts z caller's frame.
        """
        jeżeli frame jest Nic:
            frame = sys._getframe().f_back
        self.reset()
        dopóki frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        self.set_step()
        sys.settrace(self.trace_dispatch)

    def set_continue(self):
        # Don't stop wyjąwszy at przerwijpoints albo when finished
        self._set_stopinfo(self.botframe, Nic, -1)
        jeżeli nie self.breaks:
            # no przerwijpoints; run without debugger overhead
            sys.settrace(Nic)
            frame = sys._getframe().f_back
            dopóki frame oraz frame jest nie self.botframe:
                usuń frame.f_trace
                frame = frame.f_back

    def set_quit(self):
        self.stopframe = self.botframe
        self.returnframe = Nic
        self.quitting = Prawda
        sys.settrace(Nic)

    # Derived classes oraz clients can call the following methods
    # to manipulate przerwijpoints.  These methods zwróć an
    # error message jest something went wrong, Nic jeżeli all jest well.
    # Set_break prints out the przerwijpoint line oraz file:lineno.
    # Call self.get_*break*() to see the przerwijpoints albo better
    # dla bp w Breakpoint.bpbynumber: jeżeli bp: bp.bpprint().

    def set_break(self, filename, lineno, temporary=Nieprawda, cond=Nic,
                  funcname=Nic):
        filename = self.canonic(filename)
        zaimportuj linecache # Import jako late jako possible
        line = linecache.getline(filename, lineno)
        jeżeli nie line:
            zwróć 'Line %s:%d does nie exist' % (filename, lineno)
        list = self.breaks.setdefault(filename, [])
        jeżeli lineno nie w list:
            list.append(lineno)
        bp = Breakpoint(filename, lineno, temporary, cond, funcname)

    def _prune_breaks(self, filename, lineno):
        jeżeli (filename, lineno) nie w Breakpoint.bplist:
            self.breaks[filename].remove(lineno)
        jeżeli nie self.breaks[filename]:
            usuń self.breaks[filename]

    def clear_break(self, filename, lineno):
        filename = self.canonic(filename)
        jeżeli filename nie w self.breaks:
            zwróć 'There are no przerwijpoints w %s' % filename
        jeżeli lineno nie w self.breaks[filename]:
            zwróć 'There jest no przerwijpoint at %s:%d' % (filename, lineno)
        # If there's only one bp w the list dla that file,line
        # pair, then remove the przerwijs entry
        dla bp w Breakpoint.bplist[filename, lineno][:]:
            bp.deleteMe()
        self._prune_breaks(filename, lineno)

    def clear_bpbynumber(self, arg):
        spróbuj:
            bp = self.get_bpbynumber(arg)
        wyjąwszy ValueError jako err:
            zwróć str(err)
        bp.deleteMe()
        self._prune_breaks(bp.file, bp.line)

    def clear_all_file_breaks(self, filename):
        filename = self.canonic(filename)
        jeżeli filename nie w self.breaks:
            zwróć 'There are no przerwijpoints w %s' % filename
        dla line w self.breaks[filename]:
            blist = Breakpoint.bplist[filename, line]
            dla bp w blist:
                bp.deleteMe()
        usuń self.breaks[filename]

    def clear_all_breaks(self):
        jeżeli nie self.breaks:
            zwróć 'There are no przerwijpoints'
        dla bp w Breakpoint.bpbynumber:
            jeżeli bp:
                bp.deleteMe()
        self.breaks = {}

    def get_bpbynumber(self, arg):
        jeżeli nie arg:
            podnieś ValueError('Breakpoint number expected')
        spróbuj:
            number = int(arg)
        wyjąwszy ValueError:
            podnieś ValueError('Non-numeric przerwijpoint number %s' % arg)
        spróbuj:
            bp = Breakpoint.bpbynumber[number]
        wyjąwszy IndexError:
            podnieś ValueError('Breakpoint number %d out of range' % number)
        jeżeli bp jest Nic:
            podnieś ValueError('Breakpoint %d already deleted' % number)
        zwróć bp

    def get_break(self, filename, lineno):
        filename = self.canonic(filename)
        zwróć filename w self.breaks oraz \
            lineno w self.breaks[filename]

    def get_breaks(self, filename, lineno):
        filename = self.canonic(filename)
        zwróć filename w self.breaks oraz \
            lineno w self.breaks[filename] oraz \
            Breakpoint.bplist[filename, lineno] albo []

    def get_file_breaks(self, filename):
        filename = self.canonic(filename)
        jeżeli filename w self.breaks:
            zwróć self.breaks[filename]
        inaczej:
            zwróć []

    def get_all_breaks(self):
        zwróć self.breaks

    # Derived classes oraz clients can call the following method
    # to get a data structure representing a stack trace.

    def get_stack(self, f, t):
        stack = []
        jeżeli t oraz t.tb_frame jest f:
            t = t.tb_next
        dopóki f jest nie Nic:
            stack.append((f, f.f_lineno))
            jeżeli f jest self.botframe:
                przerwij
            f = f.f_back
        stack.reverse()
        i = max(0, len(stack) - 1)
        dopóki t jest nie Nic:
            stack.append((t.tb_frame, t.tb_lineno))
            t = t.tb_next
        jeżeli f jest Nic:
            i = max(0, len(stack) - 1)
        zwróć stack, i

    def format_stack_entry(self, frame_lineno, lprefix=': '):
        zaimportuj linecache, reprlib
        frame, lineno = frame_lineno
        filename = self.canonic(frame.f_code.co_filename)
        s = '%s(%r)' % (filename, lineno)
        jeżeli frame.f_code.co_name:
            s += frame.f_code.co_name
        inaczej:
            s += "<lambda>"
        jeżeli '__args__' w frame.f_locals:
            args = frame.f_locals['__args__']
        inaczej:
            args = Nic
        jeżeli args:
            s += reprlib.repr(args)
        inaczej:
            s += '()'
        jeżeli '__return__' w frame.f_locals:
            rv = frame.f_locals['__return__']
            s += '->'
            s += reprlib.repr(rv)
        line = linecache.getline(filename, lineno, frame.f_globals)
        jeżeli line:
            s += lprefix + line.strip()
        zwróć s

    # The following methods can be called by clients to use
    # a debugger to debug a statement albo an expression.
    # Both can be given jako a string, albo a code object.

    def run(self, cmd, globals=Nic, locals=Nic):
        jeżeli globals jest Nic:
            zaimportuj __main__
            globals = __main__.__dict__
        jeżeli locals jest Nic:
            locals = globals
        self.reset()
        jeżeli isinstance(cmd, str):
            cmd = compile(cmd, "<string>", "exec")
        sys.settrace(self.trace_dispatch)
        spróbuj:
            exec(cmd, globals, locals)
        wyjąwszy BdbQuit:
            dalej
        w_końcu:
            self.quitting = Prawda
            sys.settrace(Nic)

    def runeval(self, expr, globals=Nic, locals=Nic):
        jeżeli globals jest Nic:
            zaimportuj __main__
            globals = __main__.__dict__
        jeżeli locals jest Nic:
            locals = globals
        self.reset()
        sys.settrace(self.trace_dispatch)
        spróbuj:
            zwróć eval(expr, globals, locals)
        wyjąwszy BdbQuit:
            dalej
        w_końcu:
            self.quitting = Prawda
            sys.settrace(Nic)

    def runctx(self, cmd, globals, locals):
        # B/W compatibility
        self.run(cmd, globals, locals)

    # This method jest more useful to debug a single function call.

    def runcall(self, func, *args, **kwds):
        self.reset()
        sys.settrace(self.trace_dispatch)
        res = Nic
        spróbuj:
            res = func(*args, **kwds)
        wyjąwszy BdbQuit:
            dalej
        w_końcu:
            self.quitting = Prawda
            sys.settrace(Nic)
        zwróć res


def set_trace():
    Bdb().set_trace()


klasa Breakpoint:
    """Breakpoint class.

    Implements temporary przerwijpoints, ignore counts, disabling oraz
    (re)-enabling, oraz conditionals.

    Breakpoints are indexed by number through bpbynumber oraz by
    the file,line tuple using bplist.  The former points to a
    single instance of klasa Breakpoint.  The latter points to a
    list of such instances since there may be more than one
    przerwijpoint per line.

    """

    # XXX Keeping state w the klasa jest a mistake -- this means
    # you cannot have more than one active Bdb instance.

    next = 1        # Next bp to be assigned
    bplist = {}     # indexed by (file, lineno) tuple
    bpbynumber = [Nic] # Each entry jest Nic albo an instance of Bpt
                # index 0 jest unused, wyjąwszy dla marking an
                # effective przerwij .... see effective()

    def __init__(self, file, line, temporary=Nieprawda, cond=Nic, funcname=Nic):
        self.funcname = funcname
        # Needed jeżeli funcname jest nie Nic.
        self.func_first_executable_line = Nic
        self.file = file    # This better be w canonical form!
        self.line = line
        self.temporary = temporary
        self.cond = cond
        self.enabled = Prawda
        self.ignore = 0
        self.hits = 0
        self.number = Breakpoint.next
        Breakpoint.next += 1
        # Build the two lists
        self.bpbynumber.append(self)
        jeżeli (file, line) w self.bplist:
            self.bplist[file, line].append(self)
        inaczej:
            self.bplist[file, line] = [self]

    def deleteMe(self):
        index = (self.file, self.line)
        self.bpbynumber[self.number] = Nic   # No longer w list
        self.bplist[index].remove(self)
        jeżeli nie self.bplist[index]:
            # No more bp dla this f:l combo
            usuń self.bplist[index]

    def enable(self):
        self.enabled = Prawda

    def disable(self):
        self.enabled = Nieprawda

    def bpprint(self, out=Nic):
        jeżeli out jest Nic:
            out = sys.stdout
        print(self.bpformat(), file=out)

    def bpformat(self):
        jeżeli self.temporary:
            disp = 'usuń  '
        inaczej:
            disp = 'keep '
        jeżeli self.enabled:
            disp = disp + 'yes  '
        inaczej:
            disp = disp + 'no   '
        ret = '%-4dbreakpoint   %s at %s:%d' % (self.number, disp,
                                                self.file, self.line)
        jeżeli self.cond:
            ret += '\n\tstop only jeżeli %s' % (self.cond,)
        jeżeli self.ignore:
            ret += '\n\tignore next %d hits' % (self.ignore,)
        jeżeli self.hits:
            jeżeli self.hits > 1:
                ss = 's'
            inaczej:
                ss = ''
            ret += '\n\tbreakpoint already hit %d time%s' % (self.hits, ss)
        zwróć ret

    def __str__(self):
        zwróć 'breakpoint %s at %s:%s' % (self.number, self.file, self.line)

# -----------end of Breakpoint class----------

def checkfuncname(b, frame):
    """Check whether we should przerwij here because of `b.funcname`."""
    jeżeli nie b.funcname:
        # Breakpoint was set via line number.
        jeżeli b.line != frame.f_lineno:
            # Breakpoint was set at a line przy a def statement oraz the function
            # defined jest called: don't przerwij.
            zwróć Nieprawda
        zwróć Prawda

    # Breakpoint set via function name.

    jeżeli frame.f_code.co_name != b.funcname:
        # It's nie a function call, but rather execution of def statement.
        zwróć Nieprawda

    # We are w the right frame.
    jeżeli nie b.func_first_executable_line:
        # The function jest entered dla the 1st time.
        b.func_first_executable_line = frame.f_lineno

    jeżeli  b.func_first_executable_line != frame.f_lineno:
        # But we are nie at the first line number: don't przerwij.
        zwróć Nieprawda
    zwróć Prawda

# Determines jeżeli there jest an effective (active) przerwijpoint at this
# line of code.  Returns przerwijpoint number albo 0 jeżeli none
def effective(file, line, frame):
    """Determine which przerwijpoint dla this file:line jest to be acted upon.

    Called only jeżeli we know there jest a bpt at this
    location.  Returns przerwijpoint that was triggered oraz a flag
    that indicates jeżeli it jest ok to delete a temporary bp.

    """
    possibles = Breakpoint.bplist[file, line]
    dla b w possibles:
        jeżeli nie b.enabled:
            kontynuuj
        jeżeli nie checkfuncname(b, frame):
            kontynuuj
        # Count every hit when bp jest enabled
        b.hits += 1
        jeżeli nie b.cond:
            # If unconditional, oraz ignoring go on to next, inaczej przerwij
            jeżeli b.ignore > 0:
                b.ignore -= 1
                kontynuuj
            inaczej:
                # przerwijpoint oraz marker that it's ok to delete jeżeli temporary
                zwróć (b, Prawda)
        inaczej:
            # Conditional bp.
            # Ignore count applies only to those bpt hits where the
            # condition evaluates to true.
            spróbuj:
                val = eval(b.cond, frame.f_globals, frame.f_locals)
                jeżeli val:
                    jeżeli b.ignore > 0:
                        b.ignore -= 1
                        # kontynuuj
                    inaczej:
                        zwróć (b, Prawda)
                # inaczej:
                #   kontynuuj
            wyjąwszy:
                # jeżeli eval fails, most conservative thing jest to stop on
                # przerwijpoint regardless of ignore count.  Don't delete
                # temporary, jako another hint to user.
                zwróć (b, Nieprawda)
    zwróć (Nic, Nic)


# -------------------- testing --------------------

klasa Tdb(Bdb):
    def user_call(self, frame, args):
        name = frame.f_code.co_name
        jeżeli nie name: name = '???'
        print('+++ call', name, args)
    def user_line(self, frame):
        zaimportuj linecache
        name = frame.f_code.co_name
        jeżeli nie name: name = '???'
        fn = self.canonic(frame.f_code.co_filename)
        line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        print('+++', fn, frame.f_lineno, name, ':', line.strip())
    def user_return(self, frame, retval):
        print('+++ return', retval)
    def user_exception(self, frame, exc_stuff):
        print('+++ exception', exc_stuff)
        self.set_continue()

def foo(n):
    print('foo(', n, ')')
    x = bar(n*10)
    print('bar returned', x)

def bar(a):
    print('bar(', a, ')')
    zwróć a/2

def test():
    t = Tdb()
    t.run('zaimportuj bdb; bdb.foo(10)')
