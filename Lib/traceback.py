"""Extract, format oraz print information about Python stack traces."""

zaimportuj collections
zaimportuj itertools
zaimportuj linecache
zaimportuj sys

__all__ = ['extract_stack', 'extract_tb', 'format_exception',
           'format_exception_only', 'format_list', 'format_stack',
           'format_tb', 'print_exc', 'format_exc', 'print_exception',
           'print_last', 'print_stack', 'print_tb', 'clear_frames',
           'FrameSummary', 'StackSummary', 'TracebackException',
           'walk_stack', 'walk_tb']

#
# Formatting oraz printing lists of traceback lines.
#

def print_list(extracted_list, file=Nic):
    """Print the list of tuples jako returned by extract_tb() albo
    extract_stack() jako a formatted stack trace to the given file."""
    jeżeli file jest Nic:
        file = sys.stderr
    dla item w StackSummary.from_list(extracted_list).format():
        print(item, file=file, end="")

def format_list(extracted_list):
    """Format a list of traceback entry tuples dla printing.

    Given a list of tuples jako returned by extract_tb() albo
    extract_stack(), zwróć a list of strings ready dla printing.
    Each string w the resulting list corresponds to the item przy the
    same index w the argument list.  Each string ends w a newline;
    the strings may contain internal newlines jako well, dla those items
    whose source text line jest nie Nic.
    """
    zwróć StackSummary.from_list(extracted_list).format()

#
# Printing oraz Extracting Tracebacks.
#

def print_tb(tb, limit=Nic, file=Nic):
    """Print up to 'limit' stack trace entries z the traceback 'tb'.

    If 'limit' jest omitted albo Nic, all entries are printed.  If 'file'
    jest omitted albo Nic, the output goes to sys.stderr; otherwise
    'file' should be an open file albo file-like object przy a write()
    method.
    """
    print_list(extract_tb(tb, limit=limit), file=file)

def format_tb(tb, limit=Nic):
    """A shorthand dla 'format_list(extract_tb(tb, limit))'."""
    zwróć extract_tb(tb, limit=limit).format()

def extract_tb(tb, limit=Nic):
    """Return list of up to limit pre-processed entries z traceback.

    This jest useful dla alternate formatting of stack traces.  If
    'limit' jest omitted albo Nic, all entries are extracted.  A
    pre-processed stack trace entry jest a quadruple (filename, line
    number, function name, text) representing the information that jest
    usually printed dla a stack trace.  The text jest a string with
    leading oraz trailing whitespace stripped; jeżeli the source jest nie
    available it jest Nic.
    """
    zwróć StackSummary.extract(walk_tb(tb), limit=limit)

#
# Exception formatting oraz output.
#

_cause_message = (
    "\nThe above exception was the direct cause "
    "of the following exception:\n\n")

_context_message = (
    "\nDuring handling of the above exception, "
    "another exception occurred:\n\n")


def print_exception(etype, value, tb, limit=Nic, file=Nic, chain=Prawda):
    """Print exception up to 'limit' stack trace entries z 'tb' to 'file'.

    This differs z print_tb() w the following ways: (1) if
    traceback jest nie Nic, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type oraz value after the
    stack trace; (3) jeżeli type jest SyntaxError oraz value has the
    appropriate format, it prints the line where the syntax error
    occurred przy a caret on the next line indicating the approximate
    position of the error.
    """
    # format_exception has ignored etype dla some time, oraz code such jako cgitb
    # dalejes w bogus values jako a result. For compatibility przy such code we
    # ignore it here (rather than w the new TracebackException API).
    jeżeli file jest Nic:
        file = sys.stderr
    dla line w TracebackException(
            type(value), value, tb, limit=limit).format(chain=chain):
        print(line, file=file, end="")


def format_exception(etype, value, tb, limit=Nic, chain=Prawda):
    """Format a stack trace oraz the exception information.

    The arguments have the same meaning jako the corresponding arguments
    to print_exception().  The zwróć value jest a list of strings, each
    ending w a newline oraz some containing internal newlines.  When
    these lines are concatenated oraz printed, exactly the same text jest
    printed jako does print_exception().
    """
    # format_exception has ignored etype dla some time, oraz code such jako cgitb
    # dalejes w bogus values jako a result. For compatibility przy such code we
    # ignore it here (rather than w the new TracebackException API).
    zwróć list(TracebackException(
        type(value), value, tb, limit=limit).format(chain=chain))


def format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type oraz value such jako given by
    sys.last_type oraz sys.last_value. The zwróć value jest a list of
    strings, each ending w a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred jest always the last
    string w the list.

    """
    zwróć list(TracebackException(etype, value, Nic).format_exception_only())


# -- nie offical API but folk probably use these two functions.

def _format_final_exc_line(etype, value):
    valuestr = _some_str(value)
    jeżeli value == 'Nic' albo value jest Nic albo nie valuestr:
        line = "%s\n" % etype
    inaczej:
        line = "%s: %s\n" % (etype, valuestr)
    zwróć line

def _some_str(value):
    spróbuj:
        zwróć str(value)
    wyjąwszy:
        zwróć '<unprintable %s object>' % type(value).__name__

# --

def print_exc(limit=Nic, file=Nic, chain=Prawda):
    """Shorthand dla 'print_exception(*sys.exc_info(), limit, file)'."""
    print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)

def format_exc(limit=Nic, chain=Prawda):
    """Like print_exc() but zwróć a string."""
    zwróć "".join(format_exception(*sys.exc_info(), limit=limit, chain=chain))

def print_last(limit=Nic, file=Nic, chain=Prawda):
    """This jest a shorthand dla 'print_exception(sys.last_type,
    sys.last_value, sys.last_traceback, limit, file)'."""
    jeżeli nie hasattr(sys, "last_type"):
        podnieś ValueError("no last exception")
    print_exception(sys.last_type, sys.last_value, sys.last_traceback,
                    limit, file, chain)

#
# Printing oraz Extracting Stacks.
#

def print_stack(f=Nic, limit=Nic, file=Nic):
    """Print a stack trace z its invocation point.

    The optional 'f' argument can be used to specify an alternate
    stack frame at which to start. The optional 'limit' oraz 'file'
    arguments have the same meaning jako dla print_exception().
    """
    print_list(extract_stack(f, limit=limit), file=file)


def format_stack(f=Nic, limit=Nic):
    """Shorthand dla 'format_list(extract_stack(f, limit))'."""
    zwróć format_list(extract_stack(f, limit=limit))


def extract_stack(f=Nic, limit=Nic):
    """Extract the raw traceback z the current stack frame.

    The zwróć value has the same format jako dla extract_tb().  The
    optional 'f' oraz 'limit' arguments have the same meaning jako for
    print_stack().  Each item w the list jest a quadruple (filename,
    line number, function name, text), oraz the entries are w order
    z oldest to newest stack frame.
    """
    stack = StackSummary.extract(walk_stack(f), limit=limit)
    stack.reverse()
    zwróć stack


def clear_frames(tb):
    "Clear all references to local variables w the frames of a traceback."
    dopóki tb jest nie Nic:
        spróbuj:
            tb.tb_frame.clear()
        wyjąwszy RuntimeError:
            # Ignore the exception podnieśd jeżeli the frame jest still executing.
            dalej
        tb = tb.tb_next


klasa FrameSummary:
    """A single frame z a traceback.

    - :attr:`filename` The filename dla the frame.
    - :attr:`lineno` The line within filename dla the frame that was
      active when the frame was captured.
    - :attr:`name` The name of the function albo method that was executing
      when the frame was captured.
    - :attr:`line` The text z the linecache module dla the
      of code that was running when the frame was captured.
    - :attr:`locals` Either Nic jeżeli locals were nie supplied, albo a dict
      mapping the name to the repr() of the variable.
    """

    __slots__ = ('filename', 'lineno', 'name', '_line', 'locals')

    def __init__(self, filename, lineno, name, *, lookup_line=Prawda,
            locals=Nic, line=Nic):
        """Construct a FrameSummary.

        :param lookup_line: If Prawda, `linecache` jest consulted dla the source
            code line. Otherwise, the line will be looked up when first needed.
        :param locals: If supplied the frame locals, which will be captured as
            object representations.
        :param line: If provided, use this instead of looking up the line w
            the linecache.
        """
        self.filename = filename
        self.lineno = lineno
        self.name = name
        self._line = line
        jeżeli lookup_line:
            self.line
        self.locals = \
            dict((k, repr(v)) dla k, v w locals.items()) jeżeli locals inaczej Nic

    def __eq__(self, other):
        zwróć (self.filename == other.filename oraz
                self.lineno == other.lineno oraz
                self.name == other.name oraz
                self.locals == other.locals)

    def __getitem__(self, pos):
        zwróć (self.filename, self.lineno, self.name, self.line)[pos]

    def __iter__(self):
        zwróć iter([self.filename, self.lineno, self.name, self.line])

    def __repr__(self):
        zwróć "<FrameSummary file {filename}, line {lineno} w {name}>".format(
            filename=self.filename, lineno=self.lineno, name=self.name)

    @property
    def line(self):
        jeżeli self._line jest Nic:
            self._line = linecache.getline(self.filename, self.lineno).strip()
        zwróć self._line


def walk_stack(f):
    """Walk a stack uzyskajing the frame oraz line number dla each frame.

    This will follow f.f_back z the given frame. If no frame jest given, the
    current stack jest used. Usually used przy StackSummary.extract.
    """
    jeżeli f jest Nic:
        f = sys._getframe().f_back.f_back
    dopóki f jest nie Nic:
        uzyskaj f, f.f_lineno
        f = f.f_back


def walk_tb(tb):
    """Walk a traceback uzyskajing the frame oraz line number dla each frame.

    This will follow tb.tb_next (and thus jest w the opposite order to
    walk_stack). Usually used przy StackSummary.extract.
    """
    dopóki tb jest nie Nic:
        uzyskaj tb.tb_frame, tb.tb_lineno
        tb = tb.tb_next


klasa StackSummary(list):
    """A stack of frames."""

    @classmethod
    def extract(klass, frame_gen, *, limit=Nic, lookup_lines=Prawda,
            capture_locals=Nieprawda):
        """Create a StackSummary z a traceback albo stack object.

        :param frame_gen: A generator that uzyskajs (frame, lineno) tuples to
            include w the stack.
        :param limit: Nic to include all frames albo the number of frames to
            include.
        :param lookup_lines: If Prawda, lookup lines dla each frame immediately,
            otherwise lookup jest deferred until the frame jest rendered.
        :param capture_locals: If Prawda, the local variables z each frame will
            be captured jako object representations into the FrameSummary.
        """
        jeżeli limit jest Nic:
            limit = getattr(sys, 'tracebacklimit', Nic)
            jeżeli limit jest nie Nic oraz limit < 0:
                limit = 0
        jeżeli limit jest nie Nic:
            jeżeli limit >= 0:
                frame_gen = itertools.islice(frame_gen, limit)
            inaczej:
                frame_gen = collections.deque(frame_gen, maxlen=-limit)

        result = klass()
        fnames = set()
        dla f, lineno w frame_gen:
            co = f.f_code
            filename = co.co_filename
            name = co.co_name

            fnames.add(filename)
            linecache.lazycache(filename, f.f_globals)
            # Must defer line lookups until we have called checkcache.
            jeżeli capture_locals:
                f_locals = f.f_locals
            inaczej:
                f_locals = Nic
            result.append(FrameSummary(
                filename, lineno, name, lookup_line=Nieprawda, locals=f_locals))
        dla filename w fnames:
            linecache.checkcache(filename)
        # If immediate lookup was desired, trigger lookups now.
        jeżeli lookup_lines:
            dla f w result:
                f.line
        zwróć result

    @classmethod
    def from_list(klass, a_list):
        """Create a StackSummary z a simple list of tuples.

        This method supports the older Python API. Each tuple should be a
        4-tuple przy (filename, lineno, name, line) elements.
        """
        # While doing a fast-path check dla isinstance(a_list, StackSummary) jest
        # appealing, idlelib.run.cleanup_traceback oraz other similar code may
        # przerwij this by making arbitrary frames plain tuples, so we need to
        # check on a frame by frame basis.
        result = StackSummary()
        dla frame w a_list:
            jeżeli isinstance(frame, FrameSummary):
                result.append(frame)
            inaczej:
                filename, lineno, name, line = frame
                result.append(FrameSummary(filename, lineno, name, line=line))
        zwróć result

    def format(self):
        """Format the stack ready dla printing.

        Returns a list of strings ready dla printing.  Each string w the
        resulting list corresponds to a single frame z the stack.
        Each string ends w a newline; the strings may contain internal
        newlines jako well, dla those items przy source text lines.
        """
        result = []
        dla frame w self:
            row = []
            row.append('  File "{}", line {}, w {}\n'.format(
                frame.filename, frame.lineno, frame.name))
            jeżeli frame.line:
                row.append('    {}\n'.format(frame.line.strip()))
            jeżeli frame.locals:
                dla name, value w sorted(frame.locals.items()):
                    row.append('    {name} = {value}\n'.format(name=name, value=value))
            result.append(''.join(row))
        zwróć result


klasa TracebackException:
    """An exception ready dla rendering.

    The traceback module captures enough attributes z the original exception
    to this intermediary form to ensure that no references are held, while
    still being able to fully print albo format it.

    Use `from_exception` to create TracebackException instances z exception
    objects, albo the constructor to create TracebackException instances from
    individual components.

    - :attr:`__cause__` A TracebackException of the original *__cause__*.
    - :attr:`__context__` A TracebackException of the original *__context__*.
    - :attr:`__suppress_context__` The *__suppress_context__* value z the
      original exception.
    - :attr:`stack` A `StackSummary` representing the traceback.
    - :attr:`exc_type` The klasa of the original traceback.
    - :attr:`filename` For syntax errors - the filename where the error
      occured.
    - :attr:`lineno` For syntax errors - the linenumber where the error
      occured.
    - :attr:`text` For syntax errors - the text where the error
      occured.
    - :attr:`offset` For syntax errors - the offset into the text where the
      error occured.
    - :attr:`msg` For syntax errors - the compiler error message.
    """

    def __init__(self, exc_type, exc_value, exc_traceback, *, limit=Nic,
            lookup_lines=Prawda, capture_locals=Nieprawda, _seen=Nic):
        # NB: we need to accept exc_traceback, exc_value, exc_traceback to
        # permit backwards compat przy the existing API, otherwise we
        # need stub thunk objects just to glue it together.
        # Handle loops w __cause__ albo __context__.
        jeżeli _seen jest Nic:
            _seen = set()
        _seen.add(exc_value)
        # Gracefully handle (the way Python 2.4 oraz earlier did) the case of
        # being called przy no type albo value (Nic, Nic, Nic).
        jeżeli (exc_value oraz exc_value.__cause__ jest nie Nic
            oraz exc_value.__cause__ nie w _seen):
            cause = TracebackException(
                type(exc_value.__cause__),
                exc_value.__cause__,
                exc_value.__cause__.__traceback__,
                limit=limit,
                lookup_lines=Nieprawda,
                capture_locals=capture_locals,
                _seen=_seen)
        inaczej:
            cause = Nic
        jeżeli (exc_value oraz exc_value.__context__ jest nie Nic
            oraz exc_value.__context__ nie w _seen):
            context = TracebackException(
                type(exc_value.__context__),
                exc_value.__context__,
                exc_value.__context__.__traceback__,
                limit=limit,
                lookup_lines=Nieprawda,
                capture_locals=capture_locals,
                _seen=_seen)
        inaczej:
            context = Nic
        self.exc_traceback = exc_traceback
        self.__cause__ = cause
        self.__context__ = context
        self.__suppress_context__ = \
            exc_value.__suppress_context__ jeżeli exc_value inaczej Nieprawda
        # TODO: locals.
        self.stack = StackSummary.extract(
            walk_tb(exc_traceback), limit=limit, lookup_lines=lookup_lines,
            capture_locals=capture_locals)
        self.exc_type = exc_type
        # Capture now to permit freeing resources: only complication jest w the
        # unofficial API _format_final_exc_line
        self._str = _some_str(exc_value)
        jeżeli exc_type oraz issubclass(exc_type, SyntaxError):
            # Handle SyntaxError's specially
            self.filename = exc_value.filename
            self.lineno = str(exc_value.lineno)
            self.text = exc_value.text
            self.offset = exc_value.offset
            self.msg = exc_value.msg
        jeżeli lookup_lines:
            self._load_lines()

    @classmethod
    def from_exception(self, exc, *args, **kwargs):
        """Create a TracebackException z an exception."""
        zwróć TracebackException(
            type(exc), exc, exc.__traceback__, *args, **kwargs)

    def _load_lines(self):
        """Private API. force all lines w the stack to be loaded."""
        dla frame w self.stack:
            frame.line
        jeżeli self.__context__:
            self.__context__._load_lines()
        jeżeli self.__cause__:
            self.__cause__._load_lines()

    def __eq__(self, other):
        zwróć self.__dict__ == other.__dict__

    def __str__(self):
        zwróć self._str

    def format_exception_only(self):
        """Format the exception part of the traceback.

        The zwróć value jest a generator of strings, each ending w a newline.

        Normally, the generator emits a single string; however, for
        SyntaxError exceptions, it emites several lines that (when
        printed) display detailed information about where the syntax
        error occurred.

        The message indicating which exception occurred jest always the last
        string w the output.
        """
        jeżeli self.exc_type jest Nic:
            uzyskaj _format_final_exc_line(Nic, self._str)
            zwróć

        stype = self.exc_type.__qualname__
        smod = self.exc_type.__module__
        jeżeli smod nie w ("__main__", "builtins"):
            stype = smod + '.' + stype

        jeżeli nie issubclass(self.exc_type, SyntaxError):
            uzyskaj _format_final_exc_line(stype, self._str)
            zwróć

        # It was a syntax error; show exactly where the problem was found.
        filename = self.filename albo "<string>"
        lineno = str(self.lineno) albo '?'
        uzyskaj '  File "{}", line {}\n'.format(filename, lineno)

        badline = self.text
        offset = self.offset
        jeżeli badline jest nie Nic:
            uzyskaj '    {}\n'.format(badline.strip())
            jeżeli offset jest nie Nic:
                caretspace = badline.rstrip('\n')
                offset = min(len(caretspace), offset) - 1
                caretspace = caretspace[:offset].lstrip()
                # non-space whitespace (likes tabs) must be kept dla alignment
                caretspace = ((c.isspace() oraz c albo ' ') dla c w caretspace)
                uzyskaj '    {}^\n'.format(''.join(caretspace))
        msg = self.msg albo "<no detail available>"
        uzyskaj "{}: {}\n".format(stype, msg)

    def format(self, *, chain=Prawda):
        """Format the exception.

        If chain jest nie *Prawda*, *__cause__* oraz *__context__* will nie be formatted.

        The zwróć value jest a generator of strings, each ending w a newline oraz
        some containing internal newlines. `print_exception` jest a wrapper around
        this method which just prints the lines to a file.

        The message indicating which exception occurred jest always the last
        string w the output.
        """
        jeżeli chain:
            jeżeli self.__cause__ jest nie Nic:
                uzyskaj z self.__cause__.format(chain=chain)
                uzyskaj _cause_message
            albo_inaczej (self.__context__ jest nie Nic oraz
                nie self.__suppress_context__):
                uzyskaj z self.__context__.format(chain=chain)
                uzyskaj _context_message
        jeżeli self.exc_traceback jest nie Nic:
            uzyskaj 'Traceback (most recent call last):\n'
        uzyskaj z self.stack.format()
        uzyskaj z self.format_exception_only()
