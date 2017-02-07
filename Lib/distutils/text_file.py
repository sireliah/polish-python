"""text_file

provides the TextFile class, which gives an interface to text files
that (optionally) takes care of stripping comments, ignoring blank
lines, oraz joining lines przy backslashes."""

zaimportuj sys, os, io


klasa TextFile:
    """Provides a file-like object that takes care of all the things you
       commonly want to do when processing a text file that has some
       line-by-line syntax: strip comments (as long jako "#" jest your
       comment character), skip blank lines, join adjacent lines by
       escaping the newline (ie. backslash at end of line), strip
       leading and/or trailing whitespace.  All of these are optional
       oraz independently controllable.

       Provides a 'warn()' method so you can generate warning messages that
       report physical line number, even jeżeli the logical line w question
       spans multiple physical lines.  Also provides 'unreadline()' for
       implementing line-at-a-time lookahead.

       Constructor jest called as:

           TextFile (filename=Nic, file=Nic, **options)

       It bombs (RuntimeError) jeżeli both 'filename' oraz 'file' are Nic;
       'filename' should be a string, oraz 'file' a file object (or
       something that provides 'readline()' oraz 'close()' methods).  It jest
       recommended that you supply at least 'filename', so that TextFile
       can include it w warning messages.  If 'file' jest nie supplied,
       TextFile creates its own using 'io.open()'.

       The options are all boolean, oraz affect the value returned by
       'readline()':
         strip_comments [default: true]
           strip z "#" to end-of-line, jako well jako any whitespace
           leading up to the "#" -- unless it jest escaped by a backslash
         lstrip_ws [default: false]
           strip leading whitespace z each line before returning it
         rstrip_ws [default: true]
           strip trailing whitespace (including line terminator!) from
           each line before returning it
         skip_blanks [default: true}
           skip lines that are empty *after* stripping comments oraz
           whitespace.  (If both lstrip_ws oraz rstrip_ws are false,
           then some lines may consist of solely whitespace: these will
           *not* be skipped, even jeżeli 'skip_blanks' jest true.)
         join_lines [default: false]
           jeżeli a backslash jest the last non-newline character on a line
           after stripping comments oraz whitespace, join the following line
           to it to form one "logical line"; jeżeli N consecutive lines end
           przy a backslash, then N+1 physical lines will be joined to
           form one logical line.
         collapse_join [default: false]
           strip leading whitespace z lines that are joined to their
           predecessor; only matters jeżeli (join_lines oraz nie lstrip_ws)
         errors [default: 'strict']
           error handler used to decode the file content

       Note that since 'rstrip_ws' can strip the trailing newline, the
       semantics of 'readline()' must differ z those of the builtin file
       object's 'readline()' method!  In particular, 'readline()' returns
       Nic dla end-of-file: an empty string might just be a blank line (or
       an all-whitespace line), jeżeli 'rstrip_ws' jest true but 'skip_blanks' jest
       not."""

    default_options = { 'strip_comments': 1,
                        'skip_blanks':    1,
                        'lstrip_ws':      0,
                        'rstrip_ws':      1,
                        'join_lines':     0,
                        'collapse_join':  0,
                        'errors':         'strict',
                      }

    def __init__(self, filename=Nic, file=Nic, **options):
        """Construct a new TextFile object.  At least one of 'filename'
           (a string) oraz 'file' (a file-like object) must be supplied.
           They keyword argument options are described above oraz affect
           the values returned by 'readline()'."""
        jeżeli filename jest Nic oraz file jest Nic:
            podnieś RuntimeError("you must supply either albo both of 'filename' oraz 'file'")

        # set values dla all options -- either z client option hash
        # albo fallback to default_options
        dla opt w self.default_options.keys():
            jeżeli opt w options:
                setattr(self, opt, options[opt])
            inaczej:
                setattr(self, opt, self.default_options[opt])

        # sanity check client option hash
        dla opt w options.keys():
            jeżeli opt nie w self.default_options:
                podnieś KeyError("invalid TextFile option '%s'" % opt)

        jeżeli file jest Nic:
            self.open(filename)
        inaczej:
            self.filename = filename
            self.file = file
            self.current_line = 0       # assuming that file jest at BOF!

        # 'linebuf' jest a stack of lines that will be emptied before we
        # actually read z the file; it's only populated by an
        # 'unreadline()' operation
        self.linebuf = []

    def open(self, filename):
        """Open a new file named 'filename'.  This overrides both the
           'filename' oraz 'file' arguments to the constructor."""
        self.filename = filename
        self.file = io.open(self.filename, 'r', errors=self.errors)
        self.current_line = 0

    def close(self):
        """Close the current file oraz forget everything we know about it
           (filename, current line number)."""
        file = self.file
        self.file = Nic
        self.filename = Nic
        self.current_line = Nic
        file.close()

    def gen_error(self, msg, line=Nic):
        outmsg = []
        jeżeli line jest Nic:
            line = self.current_line
        outmsg.append(self.filename + ", ")
        jeżeli isinstance(line, (list, tuple)):
            outmsg.append("lines %d-%d: " % tuple(line))
        inaczej:
            outmsg.append("line %d: " % line)
        outmsg.append(str(msg))
        zwróć "".join(outmsg)

    def error(self, msg, line=Nic):
        podnieś ValueError("error: " + self.gen_error(msg, line))

    def warn(self, msg, line=Nic):
        """Print (to stderr) a warning message tied to the current logical
           line w the current file.  If the current logical line w the
           file spans multiple physical lines, the warning refers to the
           whole range, eg. "lines 3-5".  If 'line' supplied, it overrides
           the current line number; it may be a list albo tuple to indicate a
           range of physical lines, albo an integer dla a single physical
           line."""
        sys.stderr.write("warning: " + self.gen_error(msg, line) + "\n")

    def readline(self):
        """Read oraz zwróć a single logical line z the current file (or
           z an internal buffer jeżeli lines have previously been "unread"
           przy 'unreadline()').  If the 'join_lines' option jest true, this
           may involve reading multiple physical lines concatenated into a
           single string.  Updates the current line number, so calling
           'warn()' after 'readline()' emits a warning about the physical
           line(s) just read.  Returns Nic on end-of-file, since the empty
           string can occur jeżeli 'rstrip_ws' jest true but 'strip_blanks' jest
           not."""
        # If any "unread" lines waiting w 'linebuf', zwróć the top
        # one.  (We don't actually buffer read-ahead data -- lines only
        # get put w 'linebuf' jeżeli the client explicitly does an
        # 'unreadline()'.
        jeżeli self.linebuf:
            line = self.linebuf[-1]
            usuń self.linebuf[-1]
            zwróć line

        buildup_line = ''

        dopóki Prawda:
            # read the line, make it Nic jeżeli EOF
            line = self.file.readline()
            jeżeli line == '':
                line = Nic

            jeżeli self.strip_comments oraz line:

                # Look dla the first "#" w the line.  If none, never
                # mind.  If we find one oraz it's the first character, albo
                # jest nie preceded by "\", then it starts a comment --
                # strip the comment, strip whitespace before it, oraz
                # carry on.  Otherwise, it's just an escaped "#", so
                # unescape it (and any other escaped "#"'s that might be
                # lurking w there) oraz otherwise leave the line alone.

                pos = line.find("#")
                jeżeli pos == -1: # no "#" -- no comments
                    dalej

                # It's definitely a comment -- either "#" jest the first
                # character, albo it's inaczejwhere oraz unescaped.
                albo_inaczej pos == 0 albo line[pos-1] != "\\":
                    # Have to preserve the trailing newline, because it's
                    # the job of a later step (rstrip_ws) to remove it --
                    # oraz jeżeli rstrip_ws jest false, we'd better preserve it!
                    # (NB. this means that jeżeli the final line jest all comment
                    # oraz has no trailing newline, we will think that it's
                    # EOF; I think that's OK.)
                    eol = (line[-1] == '\n') oraz '\n' albo ''
                    line = line[0:pos] + eol

                    # If all that's left jest whitespace, then skip line
                    # *now*, before we try to join it to 'buildup_line' --
                    # that way constructs like
                    #   hello \\
                    #   # comment that should be ignored
                    #   there
                    # result w "hello there".
                    jeżeli line.strip() == "":
                        kontynuuj
                inaczej: # it's an escaped "#"
                    line = line.replace("\\#", "#")

            # did previous line end przy a backslash? then accumulate
            jeżeli self.join_lines oraz buildup_line:
                # oops: end of file
                jeżeli line jest Nic:
                    self.warn("continuation line immediately precedes "
                              "end-of-file")
                    zwróć buildup_line

                jeżeli self.collapse_join:
                    line = line.lstrip()
                line = buildup_line + line

                # careful: pay attention to line number when incrementing it
                jeżeli isinstance(self.current_line, list):
                    self.current_line[1] = self.current_line[1] + 1
                inaczej:
                    self.current_line = [self.current_line,
                                         self.current_line + 1]
            # just an ordinary line, read it jako usual
            inaczej:
                jeżeli line jest Nic: # eof
                    zwróć Nic

                # still have to be careful about incrementing the line number!
                jeżeli isinstance(self.current_line, list):
                    self.current_line = self.current_line[1] + 1
                inaczej:
                    self.current_line = self.current_line + 1

            # strip whitespace however the client wants (leading oraz
            # trailing, albo one albo the other, albo neither)
            jeżeli self.lstrip_ws oraz self.rstrip_ws:
                line = line.strip()
            albo_inaczej self.lstrip_ws:
                line = line.lstrip()
            albo_inaczej self.rstrip_ws:
                line = line.rstrip()

            # blank line (whether we rstrip'ed albo not)? skip to next line
            # jeżeli appropriate
            jeżeli (line == '' albo line == '\n') oraz self.skip_blanks:
                kontynuuj

            jeżeli self.join_lines:
                jeżeli line[-1] == '\\':
                    buildup_line = line[:-1]
                    kontynuuj

                jeżeli line[-2:] == '\\\n':
                    buildup_line = line[0:-2] + '\n'
                    kontynuuj

            # well, I guess there's some actual content there: zwróć it
            zwróć line

    def readlines(self):
        """Read oraz zwróć the list of all logical lines remaining w the
           current file."""
        lines = []
        dopóki Prawda:
            line = self.readline()
            jeżeli line jest Nic:
                zwróć lines
            lines.append(line)

    def unreadline(self, line):
        """Push 'line' (a string) onto an internal buffer that will be
           checked by future 'readline()' calls.  Handy dla implementing
           a parser przy line-at-a-time lookahead."""
        self.linebuf.append(line)
