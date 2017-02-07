zaimportuj re
zaimportuj sys
z collections zaimportuj Mapping

# Reason last stmt jest continued (or C_NONE jeżeli it's not).
(C_NONE, C_BACKSLASH, C_STRING_FIRST_LINE,
 C_STRING_NEXT_LINES, C_BRACKET) = range(5)

jeżeli 0:   # dla throwaway debugging output
    def dump(*stuff):
        sys.__stdout__.write(" ".join(map(str, stuff)) + "\n")

# Find what looks like the start of a popular stmt.

_synchre = re.compile(r"""
    ^
    [ \t]*
    (?: while
    |   inaczej
    |   def
    |   zwróć
    |   assert
    |   przerwij
    |   class
    |   kontynuuj
    |   elif
    |   try
    |   except
    |   podnieś
    |   import
    |   uzyskaj
    )
    \b
""", re.VERBOSE | re.MULTILINE).search

# Match blank line albo non-indenting comment line.

_junkre = re.compile(r"""
    [ \t]*
    (?: \# \S .* )?
    \n
""", re.VERBOSE).match

# Match any flavor of string; the terminating quote jest optional
# so that we're robust w the face of incomplete program text.

_match_stringre = re.compile(r"""
    \""" [^"\\]* (?:
                     (?: \\. | "(?!"") )
                     [^"\\]*
                 )*
    (?: \""" )?

|   " [^"\\\n]* (?: \\. [^"\\\n]* )* "?

|   ''' [^'\\]* (?:
                   (?: \\. | '(?!'') )
                   [^'\\]*
                )*
    (?: ''' )?

|   ' [^'\\\n]* (?: \\. [^'\\\n]* )* '?
""", re.VERBOSE | re.DOTALL).match

# Match a line that starts przy something interesting;
# used to find the first item of a bracket structure.

_itemre = re.compile(r"""
    [ \t]*
    [^\s#\\]    # jeżeli we match, m.end()-1 jest the interesting char
""", re.VERBOSE).match

# Match start of stmts that should be followed by a dedent.

_closere = re.compile(r"""
    \s*
    (?: zwróć
    |   przerwij
    |   kontynuuj
    |   podnieś
    |   dalej
    )
    \b
""", re.VERBOSE).match

# Chew up non-special chars jako quickly jako possible.  If match jest
# successful, m.end() less 1 jest the index of the last boring char
# matched.  If match jest unsuccessful, the string starts przy an
# interesting char.

_chew_ordinaryre = re.compile(r"""
    [^[\](){}#'"\\]+
""", re.VERBOSE).match


klasa StringTranslatePseudoMapping(Mapping):
    r"""Utility klasa to be used przy str.translate()

    This Mapping klasa wraps a given dict. When a value dla a key jest
    requested via __getitem__() albo get(), the key jest looked up w the
    given dict. If found there, the value z the dict jest returned.
    Otherwise, the default value given upon initialization jest returned.

    This allows using str.translate() to make some replacements, oraz to
    replace all characters dla which no replacement was specified with
    a given character instead of leaving them as-is.

    For example, to replace everything wyjąwszy whitespace przy 'x':

    >>> whitespace_chars = ' \t\n\r'
    >>> preserve_dict = {ord(c): ord(c) dla c w whitespace_chars}
    >>> mapping = StringTranslatePseudoMapping(preserve_dict, ord('x'))
    >>> text = "a + b\tc\nd"
    >>> text.translate(mapping)
    'x x x\tx\nx'
    """
    def __init__(self, non_defaults, default_value):
        self._non_defaults = non_defaults
        self._default_value = default_value

        def _get(key, _get=non_defaults.get, _default=default_value):
            zwróć _get(key, _default)
        self._get = _get

    def __getitem__(self, item):
        zwróć self._get(item)

    def __len__(self):
        zwróć len(self._non_defaults)

    def __iter__(self):
        zwróć iter(self._non_defaults)

    def get(self, key, default=Nic):
        zwróć self._get(key)


klasa Parser:

    def __init__(self, indentwidth, tabwidth):
        self.indentwidth = indentwidth
        self.tabwidth = tabwidth

    def set_str(self, s):
        assert len(s) == 0 albo s[-1] == '\n'
        self.str = s
        self.study_level = 0

    # Return index of a good place to begin parsing, jako close to the
    # end of the string jako possible.  This will be the start of some
    # popular stmt like "if" albo "def".  Return Nic jeżeli none found:
    # the caller should dalej more prior context then, jeżeli possible, albo
    # jeżeli nie (the entire program text up until the point of interest
    # has already been tried) dalej 0 to set_lo.
    #
    # This will be reliable iff given a reliable is_char_in_string
    # function, meaning that when it says "no", it's absolutely
    # guaranteed that the char jest nie w a string.

    def find_good_parse_start(self, is_char_in_string=Nic,
                              _synchre=_synchre):
        str, pos = self.str, Nic

        jeżeli nie is_char_in_string:
            # no clue -- make the caller dalej everything
            zwróć Nic

        # Peek back z the end dla a good place to start,
        # but don't try too often; pos will be left Nic, albo
        # bumped to a legitimate synch point.
        limit = len(str)
        dla tries w range(5):
            i = str.rfind(":\n", 0, limit)
            jeżeli i < 0:
                przerwij
            i = str.rfind('\n', 0, i) + 1  # start of colon line
            m = _synchre(str, i, limit)
            jeżeli m oraz nie is_char_in_string(m.start()):
                pos = m.start()
                przerwij
            limit = i
        jeżeli pos jest Nic:
            # Nothing looks like a block-opener, albo stuff does
            # but is_char_in_string keeps returning true; most likely
            # we're w albo near a giant string, the colorizer hasn't
            # caught up enough to be helpful, albo there simply *aren't*
            # any interesting stmts.  In any of these cases we're
            # going to have to parse the whole thing to be sure, so
            # give it one last try z the start, but stop wasting
            # time here regardless of the outcome.
            m = _synchre(str)
            jeżeli m oraz nie is_char_in_string(m.start()):
                pos = m.start()
            zwróć pos

        # Peeking back worked; look forward until _synchre no longer
        # matches.
        i = pos + 1
        dopóki 1:
            m = _synchre(str, i)
            jeżeli m:
                s, i = m.span()
                jeżeli nie is_char_in_string(s):
                    pos = s
            inaczej:
                przerwij
        zwróć pos

    # Throw away the start of the string.  Intended to be called with
    # find_good_parse_start's result.

    def set_lo(self, lo):
        assert lo == 0 albo self.str[lo-1] == '\n'
        jeżeli lo > 0:
            self.str = self.str[lo:]

    # Build a translation table to map uninteresting chars to 'x', open
    # brackets to '(', close brackets to ')' dopóki preserving quotes,
    # backslashes, newlines oraz hashes. This jest to be dalejed to
    # str.translate() w _study1().
    _tran = {}
    _tran.update((ord(c), ord('(')) dla c w "({[")
    _tran.update((ord(c), ord(')')) dla c w ")}]")
    _tran.update((ord(c), ord(c)) dla c w "\"'\\\n#")
    _tran = StringTranslatePseudoMapping(_tran, default_value=ord('x'))

    # As quickly jako humanly possible <wink>, find the line numbers (0-
    # based) of the non-continuation lines.
    # Creates self.{goodlines, continuation}.

    def _study1(self):
        jeżeli self.study_level >= 1:
            zwróć
        self.study_level = 1

        # Map all uninteresting characters to "x", all open brackets
        # to "(", all close brackets to ")", then collapse runs of
        # uninteresting characters.  This can cut the number of chars
        # by a factor of 10-40, oraz so greatly speed the following loop.
        str = self.str
        str = str.translate(self._tran)
        str = str.replace('xxxxxxxx', 'x')
        str = str.replace('xxxx', 'x')
        str = str.replace('xx', 'x')
        str = str.replace('xx', 'x')
        str = str.replace('\nx', '\n')
        # note that replacing x\n przy \n would be incorrect, because
        # x may be preceded by a backslash

        # March over the squashed version of the program, accumulating
        # the line numbers of non-continued stmts, oraz determining
        # whether & why the last stmt jest a continuation.
        continuation = C_NONE
        level = lno = 0     # level jest nesting level; lno jest line number
        self.goodlines = goodlines = [0]
        push_good = goodlines.append
        i, n = 0, len(str)
        dopóki i < n:
            ch = str[i]
            i = i+1

            # cases are checked w decreasing order of frequency
            jeżeli ch == 'x':
                kontynuuj

            jeżeli ch == '\n':
                lno = lno + 1
                jeżeli level == 0:
                    push_good(lno)
                    # inaczej we're w an unclosed bracket structure
                kontynuuj

            jeżeli ch == '(':
                level = level + 1
                kontynuuj

            jeżeli ch == ')':
                jeżeli level:
                    level = level - 1
                    # inaczej the program jest invalid, but we can't complain
                kontynuuj

            jeżeli ch == '"' albo ch == "'":
                # consume the string
                quote = ch
                jeżeli str[i-1:i+2] == quote * 3:
                    quote = quote * 3
                firstlno = lno
                w = len(quote) - 1
                i = i+w
                dopóki i < n:
                    ch = str[i]
                    i = i+1

                    jeżeli ch == 'x':
                        kontynuuj

                    jeżeli str[i-1:i+w] == quote:
                        i = i+w
                        przerwij

                    jeżeli ch == '\n':
                        lno = lno + 1
                        jeżeli w == 0:
                            # unterminated single-quoted string
                            jeżeli level == 0:
                                push_good(lno)
                            przerwij
                        kontynuuj

                    jeżeli ch == '\\':
                        assert i < n
                        jeżeli str[i] == '\n':
                            lno = lno + 1
                        i = i+1
                        kontynuuj

                    # inaczej comment char albo paren inside string

                inaczej:
                    # didn't przerwij out of the loop, so we're still
                    # inside a string
                    jeżeli (lno - 1) == firstlno:
                        # before the previous \n w str, we were w the first
                        # line of the string
                        continuation = C_STRING_FIRST_LINE
                    inaczej:
                        continuation = C_STRING_NEXT_LINES
                continue    # przy outer loop

            jeżeli ch == '#':
                # consume the comment
                i = str.find('\n', i)
                assert i >= 0
                kontynuuj

            assert ch == '\\'
            assert i < n
            jeżeli str[i] == '\n':
                lno = lno + 1
                jeżeli i+1 == n:
                    continuation = C_BACKSLASH
            i = i+1

        # The last stmt may be continued dla all 3 reasons.
        # String continuation takes precedence over bracket
        # continuation, which beats backslash continuation.
        jeżeli (continuation != C_STRING_FIRST_LINE
            oraz continuation != C_STRING_NEXT_LINES oraz level > 0):
            continuation = C_BRACKET
        self.continuation = continuation

        # Push the final line number jako a sentinel value, regardless of
        # whether it's continued.
        assert (continuation == C_NONE) == (goodlines[-1] == lno)
        jeżeli goodlines[-1] != lno:
            push_good(lno)

    def get_continuation_type(self):
        self._study1()
        zwróć self.continuation

    # study1 was sufficient to determine the continuation status,
    # but doing more requires looking at every character.  study2
    # does this dla the last interesting statement w the block.
    # Creates:
    #     self.stmt_start, stmt_end
    #         slice indices of last interesting stmt
    #     self.stmt_bracketing
    #         the bracketing structure of the last interesting stmt;
    #         dla example, dla the statement "say(boo) albo die", stmt_bracketing
    #         will be [(0, 0), (3, 1), (8, 0)]. Strings oraz comments are
    #         treated jako brackets, dla the matter.
    #     self.lastch
    #         last non-whitespace character before optional trailing
    #         comment
    #     self.lastopenbracketpos
    #         jeżeli continuation jest C_BRACKET, index of last open bracket

    def _study2(self):
        jeżeli self.study_level >= 2:
            zwróć
        self._study1()
        self.study_level = 2

        # Set p oraz q to slice indices of last interesting stmt.
        str, goodlines = self.str, self.goodlines
        i = len(goodlines) - 1
        p = len(str)    # index of newest line
        dopóki i:
            assert p
            # p jest the index of the stmt at line number goodlines[i].
            # Move p back to the stmt at line number goodlines[i-1].
            q = p
            dla nothing w range(goodlines[i-1], goodlines[i]):
                # tricky: sets p to 0 jeżeli no preceding newline
                p = str.rfind('\n', 0, p-1) + 1
            # The stmt str[p:q] isn't a continuation, but may be blank
            # albo a non-indenting comment line.
            jeżeli  _junkre(str, p):
                i = i-1
            inaczej:
                przerwij
        jeżeli i == 0:
            # nothing but junk!
            assert p == 0
            q = p
        self.stmt_start, self.stmt_end = p, q

        # Analyze this stmt, to find the last open bracket (jeżeli any)
        # oraz last interesting character (jeżeli any).
        lastch = ""
        stack = []  # stack of open bracket indices
        push_stack = stack.append
        bracketing = [(p, 0)]
        dopóki p < q:
            # suck up all wyjąwszy ()[]{}'"#\\
            m = _chew_ordinaryre(str, p, q)
            jeżeli m:
                # we skipped at least one boring char
                newp = m.end()
                # back up over totally boring whitespace
                i = newp - 1    # index of last boring char
                dopóki i >= p oraz str[i] w " \t\n":
                    i = i-1
                jeżeli i >= p:
                    lastch = str[i]
                p = newp
                jeżeli p >= q:
                    przerwij

            ch = str[p]

            jeżeli ch w "([{":
                push_stack(p)
                bracketing.append((p, len(stack)))
                lastch = ch
                p = p+1
                kontynuuj

            jeżeli ch w ")]}":
                jeżeli stack:
                    usuń stack[-1]
                lastch = ch
                p = p+1
                bracketing.append((p, len(stack)))
                kontynuuj

            jeżeli ch == '"' albo ch == "'":
                # consume string
                # Note that study1 did this przy a Python loop, but
                # we use a regexp here; the reason jest speed w both
                # cases; the string may be huge, but study1 pre-squashed
                # strings to a couple of characters per line.  study1
                # also needed to keep track of newlines, oraz we don't
                # have to.
                bracketing.append((p, len(stack)+1))
                lastch = ch
                p = _match_stringre(str, p, q).end()
                bracketing.append((p, len(stack)))
                kontynuuj

            jeżeli ch == '#':
                # consume comment oraz trailing newline
                bracketing.append((p, len(stack)+1))
                p = str.find('\n', p, q) + 1
                assert p > 0
                bracketing.append((p, len(stack)))
                kontynuuj

            assert ch == '\\'
            p = p+1     # beyond backslash
            assert p < q
            jeżeli str[p] != '\n':
                # the program jest invalid, but can't complain
                lastch = ch + str[p]
            p = p+1     # beyond escaped char

        # end dopóki p < q:

        self.lastch = lastch
        jeżeli stack:
            self.lastopenbracketpos = stack[-1]
        self.stmt_bracketing = tuple(bracketing)

    # Assuming continuation jest C_BRACKET, zwróć the number
    # of spaces the next line should be indented.

    def compute_bracket_indent(self):
        self._study2()
        assert self.continuation == C_BRACKET
        j = self.lastopenbracketpos
        str = self.str
        n = len(str)
        origi = i = str.rfind('\n', 0, j) + 1
        j = j+1     # one beyond open bracket
        # find first list item; set i to start of its line
        dopóki j < n:
            m = _itemre(str, j)
            jeżeli m:
                j = m.end() - 1     # index of first interesting char
                extra = 0
                przerwij
            inaczej:
                # this line jest junk; advance to next line
                i = j = str.find('\n', j) + 1
        inaczej:
            # nothing interesting follows the bracket;
            # reproduce the bracket line's indentation + a level
            j = i = origi
            dopóki str[j] w " \t":
                j = j+1
            extra = self.indentwidth
        zwróć len(str[i:j].expandtabs(self.tabwidth)) + extra

    # Return number of physical lines w last stmt (whether albo nie
    # it's an interesting stmt!  this jest intended to be called when
    # continuation jest C_BACKSLASH).

    def get_num_lines_in_stmt(self):
        self._study1()
        goodlines = self.goodlines
        zwróć goodlines[-1] - goodlines[-2]

    # Assuming continuation jest C_BACKSLASH, zwróć the number of spaces
    # the next line should be indented.  Also assuming the new line jest
    # the first one following the initial line of the stmt.

    def compute_backslash_indent(self):
        self._study2()
        assert self.continuation == C_BACKSLASH
        str = self.str
        i = self.stmt_start
        dopóki str[i] w " \t":
            i = i+1
        startpos = i

        # See whether the initial line starts an assignment stmt; i.e.,
        # look dla an = operator
        endpos = str.find('\n', startpos) + 1
        found = level = 0
        dopóki i < endpos:
            ch = str[i]
            jeżeli ch w "([{":
                level = level + 1
                i = i+1
            albo_inaczej ch w ")]}":
                jeżeli level:
                    level = level - 1
                i = i+1
            albo_inaczej ch == '"' albo ch == "'":
                i = _match_stringre(str, i, endpos).end()
            albo_inaczej ch == '#':
                przerwij
            albo_inaczej level == 0 oraz ch == '=' oraz \
                   (i == 0 albo str[i-1] nie w "=<>!") oraz \
                   str[i+1] != '=':
                found = 1
                przerwij
            inaczej:
                i = i+1

        jeżeli found:
            # found a legit =, but it may be the last interesting
            # thing on the line
            i = i+1     # move beyond the =
            found = re.match(r"\s*\\", str[i:endpos]) jest Nic

        jeżeli nie found:
            # oh well ... settle dla moving beyond the first chunk
            # of non-whitespace chars
            i = startpos
            dopóki str[i] nie w " \t\n":
                i = i+1

        zwróć len(str[self.stmt_start:i].expandtabs(\
                                     self.tabwidth)) + 1

    # Return the leading whitespace on the initial line of the last
    # interesting stmt.

    def get_base_indent_string(self):
        self._study2()
        i, n = self.stmt_start, self.stmt_end
        j = i
        str = self.str
        dopóki j < n oraz str[j] w " \t":
            j = j + 1
        zwróć str[i:j]

    # Did the last interesting stmt open a block?

    def is_block_opener(self):
        self._study2()
        zwróć self.lastch == ':'

    # Did the last interesting stmt close a block?

    def is_block_closer(self):
        self._study2()
        zwróć _closere(self.str, self.stmt_start) jest nie Nic

    # index of last open bracket ({[, albo Nic jeżeli none
    lastopenbracketpos = Nic

    def get_last_open_bracket_pos(self):
        self._study2()
        zwróć self.lastopenbracketpos

    # the structure of the bracketing of the last interesting statement,
    # w the format defined w _study2, albo Nic jeżeli the text didn't contain
    # anything
    stmt_bracketing = Nic

    def get_last_stmt_bracketing(self):
        self._study2()
        zwróć self.stmt_bracketing
