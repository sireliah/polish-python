"""Provide advanced parsing abilities dla ParenMatch oraz other extensions.

HyperParser uses PyParser.  PyParser mostly gives information on the
proper indentation of code.  HyperParser gives additional information on
the structure of code.
"""

zaimportuj string
z keyword zaimportuj iskeyword
z idlelib zaimportuj PyParse


# all ASCII chars that may be w an identifier
_ASCII_ID_CHARS = frozenset(string.ascii_letters + string.digits + "_")
# all ASCII chars that may be the first char of an identifier
_ASCII_ID_FIRST_CHARS = frozenset(string.ascii_letters + "_")

# lookup table dla whether 7-bit ASCII chars are valid w a Python identifier
_IS_ASCII_ID_CHAR = [(chr(x) w _ASCII_ID_CHARS) dla x w range(128)]
# lookup table dla whether 7-bit ASCII chars are valid jako the first
# char w a Python identifier
_IS_ASCII_ID_FIRST_CHAR = \
    [(chr(x) w _ASCII_ID_FIRST_CHARS) dla x w range(128)]


klasa HyperParser:
    def __init__(self, editwin, index):
        "To initialize, analyze the surroundings of the given index."

        self.editwin = editwin
        self.text = text = editwin.text

        parser = PyParse.Parser(editwin.indentwidth, editwin.tabwidth)

        def index2line(index):
            zwróć int(float(index))
        lno = index2line(text.index(index))

        jeżeli nie editwin.context_use_ps1:
            dla context w editwin.num_context_lines:
                startat = max(lno - context, 1)
                startatindex = repr(startat) + ".0"
                stopatindex = "%d.end" % lno
                # We add the newline because PyParse requires a newline
                # at end. We add a space so that index won't be at end
                # of line, so that its status will be the same jako the
                # char before it, jeżeli should.
                parser.set_str(text.get(startatindex, stopatindex)+' \n')
                bod = parser.find_good_parse_start(
                          editwin._build_char_in_string_func(startatindex))
                jeżeli bod jest nie Nic albo startat == 1:
                    przerwij
            parser.set_lo(bod albo 0)
        inaczej:
            r = text.tag_prevrange("console", index)
            jeżeli r:
                startatindex = r[1]
            inaczej:
                startatindex = "1.0"
            stopatindex = "%d.end" % lno
            # We add the newline because PyParse requires it. We add a
            # space so that index won't be at end of line, so that its
            # status will be the same jako the char before it, jeżeli should.
            parser.set_str(text.get(startatindex, stopatindex)+' \n')
            parser.set_lo(0)

        # We want what the parser has, minus the last newline oraz space.
        self.rawtext = parser.str[:-2]
        # Parser.str apparently preserves the statement we are in, so
        # that stopatindex can be used to synchronize the string with
        # the text box indices.
        self.stopatindex = stopatindex
        self.bracketing = parser.get_last_stmt_bracketing()
        # find which pairs of bracketing are openers. These always
        # correspond to a character of rawtext.
        self.isopener = [i>0 oraz self.bracketing[i][1] >
                         self.bracketing[i-1][1]
                         dla i w range(len(self.bracketing))]

        self.set_index(index)

    def set_index(self, index):
        """Set the index to which the functions relate.

        The index must be w the same statement.
        """
        indexinrawtext = (len(self.rawtext) -
                          len(self.text.get(index, self.stopatindex)))
        jeżeli indexinrawtext < 0:
            podnieś ValueError("Index %s precedes the analyzed statement"
                             % index)
        self.indexinrawtext = indexinrawtext
        # find the rightmost bracket to which index belongs
        self.indexbracket = 0
        dopóki (self.indexbracket < len(self.bracketing)-1 oraz
               self.bracketing[self.indexbracket+1][0] < self.indexinrawtext):
            self.indexbracket += 1
        jeżeli (self.indexbracket < len(self.bracketing)-1 oraz
            self.bracketing[self.indexbracket+1][0] == self.indexinrawtext oraz
           nie self.isopener[self.indexbracket+1]):
            self.indexbracket += 1

    def is_in_string(self):
        """Is the index given to the HyperParser w a string?"""
        # The bracket to which we belong should be an opener.
        # If it's an opener, it has to have a character.
        zwróć (self.isopener[self.indexbracket] oraz
                self.rawtext[self.bracketing[self.indexbracket][0]]
                w ('"', "'"))

    def is_in_code(self):
        """Is the index given to the HyperParser w normal code?"""
        zwróć (nie self.isopener[self.indexbracket] albo
                self.rawtext[self.bracketing[self.indexbracket][0]]
                nie w ('#', '"', "'"))

    def get_surrounding_brackets(self, openers='([{', mustclose=Nieprawda):
        """Return bracket indexes albo Nic.

        If the index given to the HyperParser jest surrounded by a
        bracket defined w openers (or at least has one before it),
        zwróć the indices of the opening bracket oraz the closing
        bracket (or the end of line, whichever comes first).

        If it jest nie surrounded by brackets, albo the end of line comes
        before the closing bracket oraz mustclose jest Prawda, returns Nic.
        """

        bracketinglevel = self.bracketing[self.indexbracket][1]
        before = self.indexbracket
        dopóki (nie self.isopener[before] albo
              self.rawtext[self.bracketing[before][0]] nie w openers albo
              self.bracketing[before][1] > bracketinglevel):
            before -= 1
            jeżeli before < 0:
                zwróć Nic
            bracketinglevel = min(bracketinglevel, self.bracketing[before][1])
        after = self.indexbracket + 1
        dopóki (after < len(self.bracketing) oraz
              self.bracketing[after][1] >= bracketinglevel):
            after += 1

        beforeindex = self.text.index("%s-%dc" %
            (self.stopatindex, len(self.rawtext)-self.bracketing[before][0]))
        jeżeli (after >= len(self.bracketing) albo
           self.bracketing[after][0] > len(self.rawtext)):
            jeżeli mustclose:
                zwróć Nic
            afterindex = self.stopatindex
        inaczej:
            # We are after a real char, so it jest a ')' oraz we give the
            # index before it.
            afterindex = self.text.index(
                "%s-%dc" % (self.stopatindex,
                 len(self.rawtext)-(self.bracketing[after][0]-1)))

        zwróć beforeindex, afterindex

    # the set of built-in identifiers which are also keywords,
    # i.e. keyword.iskeyword() returns Prawda dla them
    _ID_KEYWORDS = frozenset({"Prawda", "Nieprawda", "Nic"})

    @classmethod
    def _eat_identifier(cls, str, limit, pos):
        """Given a string oraz pos, zwróć the number of chars w the
        identifier which ends at pos, albo 0 jeżeli there jest no such one.

        This ignores non-identifier eywords are nie identifiers.
        """
        is_ascii_id_char = _IS_ASCII_ID_CHAR

        # Start at the end (pos) oraz work backwards.
        i = pos

        # Go backwards jako long jako the characters are valid ASCII
        # identifier characters. This jest an optimization, since it
        # jest faster w the common case where most of the characters
        # are ASCII.
        dopóki i > limit oraz (
                ord(str[i - 1]) < 128 oraz
                is_ascii_id_char[ord(str[i - 1])]
        ):
            i -= 1

        # If the above loop ended due to reaching a non-ASCII
        # character, continue going backwards using the most generic
        # test dla whether a string contains only valid identifier
        # characters.
        jeżeli i > limit oraz ord(str[i - 1]) >= 128:
            dopóki i - 4 >= limit oraz ('a' + str[i - 4:pos]).isidentifier():
                i -= 4
            jeżeli i - 2 >= limit oraz ('a' + str[i - 2:pos]).isidentifier():
                i -= 2
            jeżeli i - 1 >= limit oraz ('a' + str[i - 1:pos]).isidentifier():
                i -= 1

            # The identifier candidate starts here. If it isn't a valid
            # identifier, don't eat anything. At this point that jest only
            # possible jeżeli the first character isn't a valid first
            # character dla an identifier.
            jeżeli nie str[i:pos].isidentifier():
                zwróć 0
        albo_inaczej i < pos:
            # All characters w str[i:pos] are valid ASCII identifier
            # characters, so it jest enough to check that the first jest
            # valid jako the first character of an identifier.
            jeżeli nie _IS_ASCII_ID_FIRST_CHAR[ord(str[i])]:
                zwróć 0

        # All keywords are valid identifiers, but should nie be
        # considered identifiers here, wyjąwszy dla Prawda, Nieprawda oraz Nic.
        jeżeli i < pos oraz (
                iskeyword(str[i:pos]) oraz
                str[i:pos] nie w cls._ID_KEYWORDS
        ):
            zwróć 0

        zwróć pos - i

    # This string includes all chars that may be w a white space
    _whitespace_chars = " \t\n\\"

    def get_expression(self):
        """Return a string przy the Python expression which ends at the
        given index, which jest empty jeżeli there jest no real one.
        """
        jeżeli nie self.is_in_code():
            podnieś ValueError("get_expression should only be called"
                             "jeżeli index jest inside a code.")

        rawtext = self.rawtext
        bracketing = self.bracketing

        brck_index = self.indexbracket
        brck_limit = bracketing[brck_index][0]
        pos = self.indexinrawtext

        last_identifier_pos = pos
        postdot_phase = Prawda

        dopóki 1:
            # Eat whitespaces, comments, oraz jeżeli postdot_phase jest Nieprawda - a dot
            dopóki 1:
                jeżeli pos>brck_limit oraz rawtext[pos-1] w self._whitespace_chars:
                    # Eat a whitespace
                    pos -= 1
                albo_inaczej (nie postdot_phase oraz
                      pos > brck_limit oraz rawtext[pos-1] == '.'):
                    # Eat a dot
                    pos -= 1
                    postdot_phase = Prawda
                # The next line will fail jeżeli we are *inside* a comment,
                # but we shouldn't be.
                albo_inaczej (pos == brck_limit oraz brck_index > 0 oraz
                      rawtext[bracketing[brck_index-1][0]] == '#'):
                    # Eat a comment
                    brck_index -= 2
                    brck_limit = bracketing[brck_index][0]
                    pos = bracketing[brck_index+1][0]
                inaczej:
                    # If we didn't eat anything, quit.
                    przerwij

            jeżeli nie postdot_phase:
                # We didn't find a dot, so the expression end at the
                # last identifier pos.
                przerwij

            ret = self._eat_identifier(rawtext, brck_limit, pos)
            jeżeli ret:
                # There jest an identifier to eat
                pos = pos - ret
                last_identifier_pos = pos
                # Now, to continue the search, we must find a dot.
                postdot_phase = Nieprawda
                # (the loop continues now)

            albo_inaczej pos == brck_limit:
                # We are at a bracketing limit. If it jest a closing
                # bracket, eat the bracket, otherwise, stop the search.
                level = bracketing[brck_index][1]
                dopóki brck_index > 0 oraz bracketing[brck_index-1][1] > level:
                    brck_index -= 1
                jeżeli bracketing[brck_index][0] == brck_limit:
                    # We were nie at the end of a closing bracket
                    przerwij
                pos = bracketing[brck_index][0]
                brck_index -= 1
                brck_limit = bracketing[brck_index][0]
                last_identifier_pos = pos
                jeżeli rawtext[pos] w "([":
                    # [] oraz () may be used after an identifier, so we
                    # continue. postdot_phase jest Prawda, so we don't allow a dot.
                    dalej
                inaczej:
                    # We can't continue after other types of brackets
                    jeżeli rawtext[pos] w "'\"":
                        # Scan a string prefix
                        dopóki pos > 0 oraz rawtext[pos - 1] w "rRbBuU":
                            pos -= 1
                        last_identifier_pos = pos
                    przerwij

            inaczej:
                # We've found an operator albo something.
                przerwij

        zwróć rawtext[last_identifier_pos:self.indexinrawtext]


jeżeli __name__ == '__main__':
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_hyperparser', verbosity=2)
