"""Header value parser implementing various email-related RFC parsing rules.

The parsing methods defined w this module implement various email related
parsing rules.  Principal among them jest RFC 5322, which jest the followon
to RFC 2822 oraz primarily a clarification of the former.  It also implements
RFC 2047 encoded word decoding.

RFC 5322 goes to considerable trouble to maintain backward compatibility with
RFC 822 w the parse phase, dopóki cleaning up the structure on the generation
phase.  This parser supports correct RFC 5322 generation by tagging white space
as folding white space only when folding jest allowed w the non-obsolete rule
sets.  Actually, the parser jest even more generous when accepting input than RFC
5322 mandates, following the spirit of Postel's Law, which RFC 5322 encourages.
Where possible deviations z the standard are annotated on the 'defects'
attribute of tokens that deviate.

The general structure of the parser follows RFC 5322, oraz uses its terminology
where there jest a direct correspondence.  Where the implementation requires a
somewhat different structure than that used by the formal grammar, new terms
that mimic the closest existing terms are used.  Thus, it really helps to have
a copy of RFC 5322 handy when studying this code.

Input to the parser jest a string that has already been unfolded according to
RFC 5322 rules.  According to the RFC this unfolding jest the very first step, oraz
this parser leaves the unfolding step to a higher level message parser, which
will have already detected the line przerwijs that need unfolding while
determining the beginning oraz end of each header.

The output of the parser jest a TokenList object, which jest a list subclass.  A
TokenList jest a recursive data structure.  The terminal nodes of the structure
are Terminal objects, which are subclasses of str.  These do nie correspond
directly to terminal objects w the formal grammar, but are instead more
practical higher level combinations of true terminals.

All TokenList oraz Terminal objects have a 'value' attribute, which produces the
semantically meaningful value of that part of the parse subtree.  The value of
all whitespace tokens (no matter how many sub-tokens they may contain) jest a
single space, jako per the RFC rules.  This includes 'CFWS', which jest herein
included w the general klasa of whitespace tokens.  There jest one exception to
the rule that whitespace tokens are collapsed into single spaces w values: w
the value of a 'bare-quoted-string' (a quoted-string przy no leading albo
trailing whitespace), any whitespace that appeared between the quotation marks
is preserved w the returned value.  Note that w all Terminal strings quoted
pairs are turned into their unquoted values.

All TokenList oraz Terminal objects also have a string value, which attempts to
be a "canonical" representation of the RFC-compliant form of the substring that
produced the parsed subtree, including minimal use of quoted pair quoting.
Whitespace runs are nie collapsed.

Comment tokens also have a 'content' attribute providing the string found
between the parens (including any nested comments) przy whitespace preserved.

All TokenList oraz Terminal objects have a 'defects' attribute which jest a
possibly empty list all of the defects found dopóki creating the token.  Defects
may appear on any token w the tree, oraz a composite list of all defects w the
subtree jest available through the 'all_defects' attribute of any node.  (For
Terminal notes x.defects == x.all_defects.)

Each object w a parse tree jest called a 'token', oraz each has a 'token_type'
attribute that gives the name z the RFC 5322 grammar that it represents.
Not all RFC 5322 nodes are produced, oraz there jest one non-RFC 5322 node that
may be produced: 'ptext'.  A 'ptext' jest a string of printable ascii characters.
It jest returned w place of lists of (ctext/quoted-pair) oraz
(qtext/quoted-pair).

XXX: provide complete list of token types.
"""

zaimportuj re
zaimportuj urllib   # For urllib.parse.unquote
z string zaimportuj hexdigits
z collections zaimportuj OrderedDict
z operator zaimportuj itemgetter
z email zaimportuj _encoded_words jako _ew
z email zaimportuj errors
z email zaimportuj utils

#
# Useful constants oraz functions
#

WSP = set(' \t')
CFWS_LEADER = WSP | set('(')
SPECIALS = set(r'()<>@,:;.\"[]')
ATOM_ENDS = SPECIALS | WSP
DOT_ATOM_ENDS = ATOM_ENDS - set('.')
# '.', '"', oraz '(' do nie end phrases w order to support obs-phrase
PHRASE_ENDS = SPECIALS - set('."(')
TSPECIALS = (SPECIALS | set('/?=')) - set('.')
TOKEN_ENDS = TSPECIALS | WSP
ASPECIALS = TSPECIALS | set("*'%")
ATTRIBUTE_ENDS = ASPECIALS | WSP
EXTENDED_ATTRIBUTE_ENDS = ATTRIBUTE_ENDS - set('%')

def quote_string(value):
    zwróć '"'+str(value).replace('\\', '\\\\').replace('"', r'\"')+'"'

#
# Accumulator dla header folding
#

klasa _Folded:

    def __init__(self, maxlen, policy):
        self.maxlen = maxlen
        self.policy = policy
        self.lastlen = 0
        self.stickyspace = Nic
        self.firstline = Prawda
        self.done = []
        self.current = []

    def newline(self):
        self.done.extend(self.current)
        self.done.append(self.policy.linesep)
        self.current.clear()
        self.lastlen = 0

    def finalize(self):
        jeżeli self.current:
            self.newline()

    def __str__(self):
        zwróć ''.join(self.done)

    def append(self, stoken):
        self.current.append(stoken)

    def append_if_fits(self, token, stoken=Nic):
        jeżeli stoken jest Nic:
            stoken = str(token)
        l = len(stoken)
        jeżeli self.stickyspace jest nie Nic:
            stickyspace_len = len(self.stickyspace)
            jeżeli self.lastlen + stickyspace_len + l <= self.maxlen:
                self.current.append(self.stickyspace)
                self.lastlen += stickyspace_len
                self.current.append(stoken)
                self.lastlen += l
                self.stickyspace = Nic
                self.firstline = Nieprawda
                zwróć Prawda
            jeżeli token.has_fws:
                ws = token.pop_leading_fws()
                jeżeli ws jest nie Nic:
                    self.stickyspace += str(ws)
                    stickyspace_len += len(ws)
                token._fold(self)
                zwróć Prawda
            jeżeli stickyspace_len oraz l + 1 <= self.maxlen:
                margin = self.maxlen - l
                jeżeli 0 < margin < stickyspace_len:
                    trim = stickyspace_len - margin
                    self.current.append(self.stickyspace[:trim])
                    self.stickyspace = self.stickyspace[trim:]
                    stickyspace_len = trim
                self.newline()
                self.current.append(self.stickyspace)
                self.current.append(stoken)
                self.lastlen = l + stickyspace_len
                self.stickyspace = Nic
                self.firstline = Nieprawda
                zwróć Prawda
            jeżeli nie self.firstline:
                self.newline()
            self.current.append(self.stickyspace)
            self.current.append(stoken)
            self.stickyspace = Nic
            self.firstline = Nieprawda
            zwróć Prawda
        jeżeli self.lastlen + l <= self.maxlen:
            self.current.append(stoken)
            self.lastlen += l
            zwróć Prawda
        jeżeli l < self.maxlen:
            self.newline()
            self.current.append(stoken)
            self.lastlen = l
            zwróć Prawda
        zwróć Nieprawda

#
# TokenList oraz its subclasses
#

klasa TokenList(list):

    token_type = Nic

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.defects = []

    def __str__(self):
        zwróć ''.join(str(x) dla x w self)

    def __repr__(self):
        zwróć '{}({})'.format(self.__class__.__name__,
                             super().__repr__())

    @property
    def value(self):
        zwróć ''.join(x.value dla x w self jeżeli x.value)

    @property
    def all_defects(self):
        zwróć sum((x.all_defects dla x w self), self.defects)

    #
    # Folding API
    #
    # parts():
    #
    # zwróć a list of objects that constitute the "higher level syntactic
    # objects" specified by the RFC jako the best places to fold a header line.
    # The returned objects must include leading folding white space, even if
    # this means mutating the underlying parse tree of the object.  Each object
    # jest only responsible dla returning *its* parts, oraz should nie drill down
    # to any lower level wyjąwszy jako required to meet the leading folding white
    # space constraint.
    #
    # _fold(folded):
    #
    #   folded: the result accumulator.  This jest an instance of _Folded.
    #       (XXX: I haven't finished factoring this out yet, the folding code
    #       pretty much uses this jako a state object.) When the folded.current
    #       contains jako much text jako will fit, the _fold method should call
    #       folded.newline.
    #  folded.lastlen: the current length of the test stored w folded.current.
    #  folded.maxlen: The maximum number of characters that may appear on a
    #       folded line.  Differs z the policy setting w that "no limit" jest
    #       represented by +inf, which means it can be used w the trivially
    #       logical fashion w comparisons.
    #
    # Currently no subclasses implement parts, oraz I think this will remain
    # true.  A subclass only needs to implement _fold when the generic version
    # isn't sufficient.  _fold will need to be implemented primarily when it jest
    # possible dla encoded words to appear w the specialized token-list, since
    # there jest no generic algorithm that can know where exactly the encoded
    # words are allowed.  A _fold implementation jest responsible dla filling
    # lines w the same general way that the top level _fold does. It may, oraz
    # should, call the _fold method of sub-objects w a similar fashion to that
    # of the top level _fold.
    #
    # XXX: I'm hoping it will be possible to factor the existing code further
    # to reduce redundancy oraz make the logic clearer.

    @property
    def parts(self):
        klass = self.__class__
        this = []
        dla token w self:
            jeżeli token.startswith_fws():
                jeżeli this:
                    uzyskaj this[0] jeżeli len(this)==1 inaczej klass(this)
                    this.clear()
            end_ws = token.pop_trailing_ws()
            this.append(token)
            jeżeli end_ws:
                uzyskaj klass(this)
                this = [end_ws]
        jeżeli this:
            uzyskaj this[0] jeżeli len(this)==1 inaczej klass(this)

    def startswith_fws(self):
        zwróć self[0].startswith_fws()

    def pop_leading_fws(self):
        jeżeli self[0].token_type == 'fws':
            zwróć self.pop(0)
        zwróć self[0].pop_leading_fws()

    def pop_trailing_ws(self):
        jeżeli self[-1].token_type == 'cfws':
            zwróć self.pop(-1)
        zwróć self[-1].pop_trailing_ws()

    @property
    def has_fws(self):
        dla part w self:
            jeżeli part.has_fws:
                zwróć Prawda
        zwróć Nieprawda

    def has_leading_comment(self):
        zwróć self[0].has_leading_comment()

    @property
    def comments(self):
        comments = []
        dla token w self:
            comments.extend(token.comments)
        zwróć comments

    def fold(self, *, policy):
        # max_line_length 0/Nic means no limit, ie: infinitely long.
        maxlen = policy.max_line_length albo float("+inf")
        folded = _Folded(maxlen, policy)
        self._fold(folded)
        folded.finalize()
        zwróć str(folded)

    def as_encoded_word(self, charset):
        # This works only dla things returned by 'parts', which include
        # the leading fws, jeżeli any, that should be used.
        res = []
        ws = self.pop_leading_fws()
        jeżeli ws:
            res.append(ws)
        trailer = self.pop(-1) jeżeli self[-1].token_type=='fws' inaczej ''
        res.append(_ew.encode(str(self), charset))
        res.append(trailer)
        zwróć ''.join(res)

    def cte_encode(self, charset, policy):
        res = []
        dla part w self:
            res.append(part.cte_encode(charset, policy))
        zwróć ''.join(res)

    def _fold(self, folded):
        encoding = 'utf-8' jeżeli folded.policy.utf8 inaczej 'ascii'
        dla part w self.parts:
            tstr = str(part)
            tlen = len(tstr)
            spróbuj:
                str(part).encode(encoding)
            wyjąwszy UnicodeEncodeError:
                jeżeli any(isinstance(x, errors.UndecodableBytesDefect)
                        dla x w part.all_defects):
                    charset = 'unknown-8bit'
                inaczej:
                    # XXX: this should be a policy setting when utf8 jest Nieprawda.
                    charset = 'utf-8'
                tstr = part.cte_encode(charset, folded.policy)
                tlen = len(tstr)
            jeżeli folded.append_if_fits(part, tstr):
                kontynuuj
            # Peel off the leading whitespace jeżeli any oraz make it sticky, to
            # avoid infinite recursion.
            ws = part.pop_leading_fws()
            jeżeli ws jest nie Nic:
                # Peel off the leading whitespace oraz make it sticky, to
                # avoid infinite recursion.
                folded.stickyspace = str(part.pop(0))
                jeżeli folded.append_if_fits(part):
                    kontynuuj
            jeżeli part.has_fws:
                part._fold(folded)
                kontynuuj
            # There are no fold points w this one; it jest too long dla a single
            # line oraz can't be split...we just have to put it on its own line.
            folded.append(tstr)
            folded.newline()

    def pprint(self, indent=''):
        print('\n'.join(self._pp(indent='')))

    def ppstr(self, indent=''):
        zwróć '\n'.join(self._pp(indent=''))

    def _pp(self, indent=''):
        uzyskaj '{}{}/{}('.format(
            indent,
            self.__class__.__name__,
            self.token_type)
        dla token w self:
            jeżeli nie hasattr(token, '_pp'):
                uzyskaj (indent + '    !! invalid element w token '
                                        'list: {!r}'.format(token))
            inaczej:
                uzyskaj z token._pp(indent+'    ')
        jeżeli self.defects:
            extra = ' Defects: {}'.format(self.defects)
        inaczej:
            extra = ''
        uzyskaj '{}){}'.format(indent, extra)


klasa WhiteSpaceTokenList(TokenList):

    @property
    def value(self):
        zwróć ' '

    @property
    def comments(self):
        zwróć [x.content dla x w self jeżeli x.token_type=='comment']


klasa UnstructuredTokenList(TokenList):

    token_type = 'unstructured'

    def _fold(self, folded):
        last_ew = Nic
        encoding = 'utf-8' jeżeli folded.policy.utf8 inaczej 'ascii'
        dla part w self.parts:
            tstr = str(part)
            is_ew = Nieprawda
            spróbuj:
                str(part).encode(encoding)
            wyjąwszy UnicodeEncodeError:
                jeżeli any(isinstance(x, errors.UndecodableBytesDefect)
                       dla x w part.all_defects):
                    charset = 'unknown-8bit'
                inaczej:
                    charset = 'utf-8'
                jeżeli last_ew jest nie Nic:
                    # We've already done an EW, combine this one przy it
                    # jeżeli there's room.
                    chunk = get_unstructured(
                        ''.join(folded.current[last_ew:]+[tstr])).as_encoded_word(charset)
                    oldlastlen = sum(len(x) dla x w folded.current[:last_ew])
                    schunk = str(chunk)
                    lchunk = len(schunk)
                    jeżeli oldlastlen + lchunk <= folded.maxlen:
                        usuń folded.current[last_ew:]
                        folded.append(schunk)
                        folded.lastlen = oldlastlen + lchunk
                        kontynuuj
                tstr = part.as_encoded_word(charset)
                is_ew = Prawda
            jeżeli folded.append_if_fits(part, tstr):
                jeżeli is_ew:
                    last_ew = len(folded.current) - 1
                kontynuuj
            jeżeli is_ew albo last_ew:
                # It's too big to fit on the line, but since we've
                # got encoded words we can use encoded word folding.
                part._fold_as_ew(folded)
                kontynuuj
            # Peel off the leading whitespace jeżeli any oraz make it sticky, to
            # avoid infinite recursion.
            ws = part.pop_leading_fws()
            jeżeli ws jest nie Nic:
                folded.stickyspace = str(ws)
                jeżeli folded.append_if_fits(part):
                    kontynuuj
            jeżeli part.has_fws:
                part.fold(folded)
                kontynuuj
            # It can't be split...we just have to put it on its own line.
            folded.append(tstr)
            folded.newline()
            last_ew = Nic

    def cte_encode(self, charset, policy):
        res = []
        last_ew = Nic
        dla part w self:
            spart = str(part)
            spróbuj:
                spart.encode('us-ascii')
                res.append(spart)
            wyjąwszy UnicodeEncodeError:
                jeżeli last_ew jest Nic:
                    res.append(part.cte_encode(charset, policy))
                    last_ew = len(res)
                inaczej:
                    tl = get_unstructured(''.join(res[last_ew:] + [spart]))
                    res.append(tl.as_encoded_word())
        zwróć ''.join(res)


klasa Phrase(TokenList):

    token_type = 'phrase'

    def _fold(self, folded):
        # As przy Unstructured, we can have pure ASCII przy albo without
        # surrogateescape encoded bytes, albo we could have unicode.  But this
        # case jest more complicated, since we have to deal przy the various
        # sub-token types oraz how they can be composed w the face of
        # unicode-that-needs-CTE-encoding, oraz the fact that jeżeli a token a
        # comment that becomes a barrier across which we can't compose encoded
        # words.
        last_ew = Nic
        encoding = 'utf-8' jeżeli folded.policy.utf8 inaczej 'ascii'
        dla part w self.parts:
            tstr = str(part)
            tlen = len(tstr)
            has_ew = Nieprawda
            spróbuj:
                str(part).encode(encoding)
            wyjąwszy UnicodeEncodeError:
                jeżeli any(isinstance(x, errors.UndecodableBytesDefect)
                        dla x w part.all_defects):
                    charset = 'unknown-8bit'
                inaczej:
                    charset = 'utf-8'
                jeżeli last_ew jest nie Nic oraz nie part.has_leading_comment():
                    # We've already done an EW, let's see jeżeli we can combine
                    # this one przy it.  The last_ew logic ensures that all we
                    # have at this point jest atoms, no comments albo quoted
                    # strings.  So we can treat the text between the last
                    # encoded word oraz the content of this token as
                    # unstructured text, oraz things will work correctly.  But
                    # we have to strip off any trailing comment on this token
                    # first, oraz jeżeli it jest a quoted string we have to pull out
                    # the content (we're encoding it, so it no longer needs to
                    # be quoted).
                    jeżeli part[-1].token_type == 'cfws' oraz part.comments:
                        remainder = part.pop(-1)
                    inaczej:
                        remainder = ''
                    dla i, token w enumerate(part):
                        jeżeli token.token_type == 'bare-quoted-string':
                            part[i] = UnstructuredTokenList(token[:])
                    chunk = get_unstructured(
                        ''.join(folded.current[last_ew:]+[tstr])).as_encoded_word(charset)
                    schunk = str(chunk)
                    lchunk = len(schunk)
                    jeżeli last_ew + lchunk <= folded.maxlen:
                        usuń folded.current[last_ew:]
                        folded.append(schunk)
                        folded.lastlen = sum(len(x) dla x w folded.current)
                        kontynuuj
                tstr = part.as_encoded_word(charset)
                tlen = len(tstr)
                has_ew = Prawda
            jeżeli folded.append_if_fits(part, tstr):
                jeżeli has_ew oraz nie part.comments:
                    last_ew = len(folded.current) - 1
                albo_inaczej part.comments albo part.token_type == 'quoted-string':
                    # If a comment jest involved we can't combine EWs.  And jeżeli a
                    # quoted string jest involved, it's nie worth the effort to
                    # try to combine them.
                    last_ew = Nic
                kontynuuj
            part._fold(folded)

    def cte_encode(self, charset, policy):
        res = []
        last_ew = Nic
        is_ew = Nieprawda
        dla part w self:
            spart = str(part)
            spróbuj:
                spart.encode('us-ascii')
                res.append(spart)
            wyjąwszy UnicodeEncodeError:
                is_ew = Prawda
                jeżeli last_ew jest Nic:
                    jeżeli nie part.comments:
                        last_ew = len(res)
                    res.append(part.cte_encode(charset, policy))
                albo_inaczej nie part.has_leading_comment():
                    jeżeli part[-1].token_type == 'cfws' oraz part.comments:
                        remainder = part.pop(-1)
                    inaczej:
                        remainder = ''
                    dla i, token w enumerate(part):
                        jeżeli token.token_type == 'bare-quoted-string':
                            part[i] = UnstructuredTokenList(token[:])
                    tl = get_unstructured(''.join(res[last_ew:] + [spart]))
                    res[last_ew:] = [tl.as_encoded_word(charset)]
            jeżeli part.comments albo (nie is_ew oraz part.token_type == 'quoted-string'):
                last_ew = Nic
        zwróć ''.join(res)

klasa Word(TokenList):

    token_type = 'word'


klasa CFWSList(WhiteSpaceTokenList):

    token_type = 'cfws'

    def has_leading_comment(self):
        zwróć bool(self.comments)


klasa Atom(TokenList):

    token_type = 'atom'


klasa Token(TokenList):

    token_type = 'token'


klasa EncodedWord(TokenList):

    token_type = 'encoded-word'
    cte = Nic
    charset = Nic
    lang = Nic

    @property
    def encoded(self):
        jeżeli self.cte jest nie Nic:
            zwróć self.cte
        _ew.encode(str(self), self.charset)



klasa QuotedString(TokenList):

    token_type = 'quoted-string'

    @property
    def content(self):
        dla x w self:
            jeżeli x.token_type == 'bare-quoted-string':
                zwróć x.value

    @property
    def quoted_value(self):
        res = []
        dla x w self:
            jeżeli x.token_type == 'bare-quoted-string':
                res.append(str(x))
            inaczej:
                res.append(x.value)
        zwróć ''.join(res)

    @property
    def stripped_value(self):
        dla token w self:
            jeżeli token.token_type == 'bare-quoted-string':
                zwróć token.value


klasa BareQuotedString(QuotedString):

    token_type = 'bare-quoted-string'

    def __str__(self):
        zwróć quote_string(''.join(str(x) dla x w self))

    @property
    def value(self):
        zwróć ''.join(str(x) dla x w self)


klasa Comment(WhiteSpaceTokenList):

    token_type = 'comment'

    def __str__(self):
        zwróć ''.join(sum([
                            ["("],
                            [self.quote(x) dla x w self],
                            [")"],
                            ], []))

    def quote(self, value):
        jeżeli value.token_type == 'comment':
            zwróć str(value)
        zwróć str(value).replace('\\', '\\\\').replace(
                                  '(', '\(').replace(
                                  ')', '\)')

    @property
    def content(self):
        zwróć ''.join(str(x) dla x w self)

    @property
    def comments(self):
        zwróć [self.content]

klasa AddressList(TokenList):

    token_type = 'address-list'

    @property
    def addresses(self):
        zwróć [x dla x w self jeżeli x.token_type=='address']

    @property
    def mailboxes(self):
        zwróć sum((x.mailboxes
                    dla x w self jeżeli x.token_type=='address'), [])

    @property
    def all_mailboxes(self):
        zwróć sum((x.all_mailboxes
                    dla x w self jeżeli x.token_type=='address'), [])


klasa Address(TokenList):

    token_type = 'address'

    @property
    def display_name(self):
        jeżeli self[0].token_type == 'group':
            zwróć self[0].display_name

    @property
    def mailboxes(self):
        jeżeli self[0].token_type == 'mailbox':
            zwróć [self[0]]
        albo_inaczej self[0].token_type == 'invalid-mailbox':
            zwróć []
        zwróć self[0].mailboxes

    @property
    def all_mailboxes(self):
        jeżeli self[0].token_type == 'mailbox':
            zwróć [self[0]]
        albo_inaczej self[0].token_type == 'invalid-mailbox':
            zwróć [self[0]]
        zwróć self[0].all_mailboxes

klasa MailboxList(TokenList):

    token_type = 'mailbox-list'

    @property
    def mailboxes(self):
        zwróć [x dla x w self jeżeli x.token_type=='mailbox']

    @property
    def all_mailboxes(self):
        zwróć [x dla x w self
            jeżeli x.token_type w ('mailbox', 'invalid-mailbox')]


klasa GroupList(TokenList):

    token_type = 'group-list'

    @property
    def mailboxes(self):
        jeżeli nie self albo self[0].token_type != 'mailbox-list':
            zwróć []
        zwróć self[0].mailboxes

    @property
    def all_mailboxes(self):
        jeżeli nie self albo self[0].token_type != 'mailbox-list':
            zwróć []
        zwróć self[0].all_mailboxes


klasa Group(TokenList):

    token_type = "group"

    @property
    def mailboxes(self):
        jeżeli self[2].token_type != 'group-list':
            zwróć []
        zwróć self[2].mailboxes

    @property
    def all_mailboxes(self):
        jeżeli self[2].token_type != 'group-list':
            zwróć []
        zwróć self[2].all_mailboxes

    @property
    def display_name(self):
        zwróć self[0].display_name


klasa NameAddr(TokenList):

    token_type = 'name-addr'

    @property
    def display_name(self):
        jeżeli len(self) == 1:
            zwróć Nic
        zwróć self[0].display_name

    @property
    def local_part(self):
        zwróć self[-1].local_part

    @property
    def domain(self):
        zwróć self[-1].domain

    @property
    def route(self):
        zwróć self[-1].route

    @property
    def addr_spec(self):
        zwróć self[-1].addr_spec


klasa AngleAddr(TokenList):

    token_type = 'angle-addr'

    @property
    def local_part(self):
        dla x w self:
            jeżeli x.token_type == 'addr-spec':
                zwróć x.local_part

    @property
    def domain(self):
        dla x w self:
            jeżeli x.token_type == 'addr-spec':
                zwróć x.domain

    @property
    def route(self):
        dla x w self:
            jeżeli x.token_type == 'obs-route':
                zwróć x.domains

    @property
    def addr_spec(self):
        dla x w self:
            jeżeli x.token_type == 'addr-spec':
                zwróć x.addr_spec
        inaczej:
            zwróć '<>'


klasa ObsRoute(TokenList):

    token_type = 'obs-route'

    @property
    def domains(self):
        zwróć [x.domain dla x w self jeżeli x.token_type == 'domain']


klasa Mailbox(TokenList):

    token_type = 'mailbox'

    @property
    def display_name(self):
        jeżeli self[0].token_type == 'name-addr':
            zwróć self[0].display_name

    @property
    def local_part(self):
        zwróć self[0].local_part

    @property
    def domain(self):
        zwróć self[0].domain

    @property
    def route(self):
        jeżeli self[0].token_type == 'name-addr':
            zwróć self[0].route

    @property
    def addr_spec(self):
        zwróć self[0].addr_spec


klasa InvalidMailbox(TokenList):

    token_type = 'invalid-mailbox'

    @property
    def display_name(self):
        zwróć Nic

    local_part = domain = route = addr_spec = display_name


klasa Domain(TokenList):

    token_type = 'domain'

    @property
    def domain(self):
        zwróć ''.join(super().value.split())


klasa DotAtom(TokenList):

    token_type = 'dot-atom'


klasa DotAtomText(TokenList):

    token_type = 'dot-atom-text'


klasa AddrSpec(TokenList):

    token_type = 'addr-spec'

    @property
    def local_part(self):
        zwróć self[0].local_part

    @property
    def domain(self):
        jeżeli len(self) < 3:
            zwróć Nic
        zwróć self[-1].domain

    @property
    def value(self):
        jeżeli len(self) < 3:
            zwróć self[0].value
        zwróć self[0].value.rstrip()+self[1].value+self[2].value.lstrip()

    @property
    def addr_spec(self):
        nameset = set(self.local_part)
        jeżeli len(nameset) > len(nameset-DOT_ATOM_ENDS):
            lp = quote_string(self.local_part)
        inaczej:
            lp = self.local_part
        jeżeli self.domain jest nie Nic:
            zwróć lp + '@' + self.domain
        zwróć lp


klasa ObsLocalPart(TokenList):

    token_type = 'obs-local-part'


klasa DisplayName(Phrase):

    token_type = 'display-name'

    @property
    def display_name(self):
        res = TokenList(self)
        jeżeli res[0].token_type == 'cfws':
            res.pop(0)
        inaczej:
            jeżeli res[0][0].token_type == 'cfws':
                res[0] = TokenList(res[0][1:])
        jeżeli res[-1].token_type == 'cfws':
            res.pop()
        inaczej:
            jeżeli res[-1][-1].token_type == 'cfws':
                res[-1] = TokenList(res[-1][:-1])
        zwróć res.value

    @property
    def value(self):
        quote = Nieprawda
        jeżeli self.defects:
            quote = Prawda
        inaczej:
            dla x w self:
                jeżeli x.token_type == 'quoted-string':
                    quote = Prawda
        jeżeli quote:
            pre = post = ''
            jeżeli self[0].token_type=='cfws' albo self[0][0].token_type=='cfws':
                pre = ' '
            jeżeli self[-1].token_type=='cfws' albo self[-1][-1].token_type=='cfws':
                post = ' '
            zwróć pre+quote_string(self.display_name)+post
        inaczej:
            zwróć super().value


klasa LocalPart(TokenList):

    token_type = 'local-part'

    @property
    def value(self):
        jeżeli self[0].token_type == "quoted-string":
            zwróć self[0].quoted_value
        inaczej:
            zwróć self[0].value

    @property
    def local_part(self):
        # Strip whitespace z front, back, oraz around dots.
        res = [DOT]
        last = DOT
        last_is_tl = Nieprawda
        dla tok w self[0] + [DOT]:
            jeżeli tok.token_type == 'cfws':
                kontynuuj
            jeżeli (last_is_tl oraz tok.token_type == 'dot' oraz
                    last[-1].token_type == 'cfws'):
                res[-1] = TokenList(last[:-1])
            is_tl = isinstance(tok, TokenList)
            jeżeli (is_tl oraz last.token_type == 'dot' oraz
                    tok[0].token_type == 'cfws'):
                res.append(TokenList(tok[1:]))
            inaczej:
                res.append(tok)
            last = res[-1]
            last_is_tl = is_tl
        res = TokenList(res[1:-1])
        zwróć res.value


klasa DomainLiteral(TokenList):

    token_type = 'domain-literal'

    @property
    def domain(self):
        zwróć ''.join(super().value.split())

    @property
    def ip(self):
        dla x w self:
            jeżeli x.token_type == 'ptext':
                zwróć x.value


klasa MIMEVersion(TokenList):

    token_type = 'mime-version'
    major = Nic
    minor = Nic


klasa Parameter(TokenList):

    token_type = 'parameter'
    sectioned = Nieprawda
    extended = Nieprawda
    charset = 'us-ascii'

    @property
    def section_number(self):
        # Because the first token, the attribute (name) eats CFWS, the second
        # token jest always the section jeżeli there jest one.
        zwróć self[1].number jeżeli self.sectioned inaczej 0

    @property
    def param_value(self):
        # This jest part of the "handle quoted extended parameters" hack.
        dla token w self:
            jeżeli token.token_type == 'value':
                zwróć token.stripped_value
            jeżeli token.token_type == 'quoted-string':
                dla token w token:
                    jeżeli token.token_type == 'bare-quoted-string':
                        dla token w token:
                            jeżeli token.token_type == 'value':
                                zwróć token.stripped_value
        zwróć ''


klasa InvalidParameter(Parameter):

    token_type = 'invalid-parameter'


klasa Attribute(TokenList):

    token_type = 'attribute'

    @property
    def stripped_value(self):
        dla token w self:
            jeżeli token.token_type.endswith('attrtext'):
                zwróć token.value

klasa Section(TokenList):

    token_type = 'section'
    number = Nic


klasa Value(TokenList):

    token_type = 'value'

    @property
    def stripped_value(self):
        token = self[0]
        jeżeli token.token_type == 'cfws':
            token = self[1]
        jeżeli token.token_type.endswith(
                ('quoted-string', 'attribute', 'extended-attribute')):
            zwróć token.stripped_value
        zwróć self.value


klasa MimeParameters(TokenList):

    token_type = 'mime-parameters'

    @property
    def params(self):
        # The RFC specifically states that the ordering of parameters jest nie
        # guaranteed oraz may be reordered by the transport layer.  So we have
        # to assume the RFC 2231 pieces can come w any order.  However, we
        # output them w the order that we first see a given name, which gives
        # us a stable __str__.
        params = OrderedDict()
        dla token w self:
            jeżeli nie token.token_type.endswith('parameter'):
                kontynuuj
            jeżeli token[0].token_type != 'attribute':
                kontynuuj
            name = token[0].value.strip()
            jeżeli name nie w params:
                params[name] = []
            params[name].append((token.section_number, token))
        dla name, parts w params.items():
            parts = sorted(parts, key=itemgetter(0))
            first_param = parts[0][1]
            charset = first_param.charset
            # Our arbitrary error recovery jest to ignore duplicate parameters,
            # to use appearance order jeżeli there are duplicate rfc 2231 parts,
            # oraz to ignore gaps.  This mimics the error recovery of get_param.
            jeżeli nie first_param.extended oraz len(parts) > 1:
                jeżeli parts[1][0] == 0:
                    parts[1][1].defects.append(errors.InvalidHeaderDefect(
                        'duplicate parameter name; duplicate(s) ignored'))
                    parts = parts[:1]
                # Else assume the *0* was missing...note that this jest different
                # z get_param, but we registered a defect dla this earlier.
            value_parts = []
            i = 0
            dla section_number, param w parts:
                jeżeli section_number != i:
                    # We could get fancier here oraz look dla a complete
                    # duplicate extended parameter oraz ignore the second one
                    # seen.  But we're nie doing that.  The old code didn't.
                    jeżeli nie param.extended:
                        param.defects.append(errors.InvalidHeaderDefect(
                            'duplicate parameter name; duplicate ignored'))
                        kontynuuj
                    inaczej:
                        param.defects.append(errors.InvalidHeaderDefect(
                            "inconsistent RFC2231 parameter numbering"))
                i += 1
                value = param.param_value
                jeżeli param.extended:
                    spróbuj:
                        value = urllib.parse.unquote_to_bytes(value)
                    wyjąwszy UnicodeEncodeError:
                        # source had surrogate escaped bytes.  What we do now
                        # jest a bit of an open question.  I'm nie sure this jest
                        # the best choice, but it jest what the old algorithm did
                        value = urllib.parse.unquote(value, encoding='latin-1')
                    inaczej:
                        spróbuj:
                            value = value.decode(charset, 'surrogateescape')
                        wyjąwszy LookupError:
                            # XXX: there should really be a custom defect for
                            # unknown character set to make it easy to find,
                            # because otherwise unknown charset jest a silent
                            # failure.
                            value = value.decode('us-ascii', 'surrogateescape')
                        jeżeli utils._has_surrogates(value):
                            param.defects.append(errors.UndecodableBytesDefect())
                value_parts.append(value)
            value = ''.join(value_parts)
            uzyskaj name, value

    def __str__(self):
        params = []
        dla name, value w self.params:
            jeżeli value:
                params.append('{}={}'.format(name, quote_string(value)))
            inaczej:
                params.append(name)
        params = '; '.join(params)
        zwróć ' ' + params jeżeli params inaczej ''


klasa ParameterizedHeaderValue(TokenList):

    @property
    def params(self):
        dla token w reversed(self):
            jeżeli token.token_type == 'mime-parameters':
                zwróć token.params
        zwróć {}

    @property
    def parts(self):
        jeżeli self oraz self[-1].token_type == 'mime-parameters':
            # We don't want to start a new line jeżeli all of the params don't fit
            # after the value, so unwrap the parameter list.
            zwróć TokenList(self[:-1] + self[-1])
        zwróć TokenList(self).parts


klasa ContentType(ParameterizedHeaderValue):

    token_type = 'content-type'
    maintype = 'text'
    subtype = 'plain'


klasa ContentDisposition(ParameterizedHeaderValue):

    token_type = 'content-disposition'
    content_disposition = Nic


klasa ContentTransferEncoding(TokenList):

    token_type = 'content-transfer-encoding'
    cte = '7bit'


klasa HeaderLabel(TokenList):

    token_type = 'header-label'


klasa Header(TokenList):

    token_type = 'header'

    def _fold(self, folded):
        folded.append(str(self.pop(0)))
        folded.lastlen = len(folded.current[0])
        # The first line of the header jest different z all others: we don't
        # want to start a new object on a new line jeżeli it has any fold points w
        # it that would allow part of it to be on the first header line.
        # Further, jeżeli the first fold point would fit on the new line, we want
        # to do that, but jeżeli it doesn't we want to put it on the first line.
        # Folded supports this via the stickyspace attribute.  If this
        # attribute jest nie Nic, it does the special handling.
        folded.stickyspace = str(self.pop(0)) jeżeli self[0].token_type == 'cfws' inaczej ''
        rest = self.pop(0)
        jeżeli self:
            podnieś ValueError("Malformed Header token list")
        rest._fold(folded)


#
# Terminal classes oraz instances
#

klasa Terminal(str):

    def __new__(cls, value, token_type):
        self = super().__new__(cls, value)
        self.token_type = token_type
        self.defects = []
        zwróć self

    def __repr__(self):
        zwróć "{}({})".format(self.__class__.__name__, super().__repr__())

    @property
    def all_defects(self):
        zwróć list(self.defects)

    def _pp(self, indent=''):
        zwróć ["{}{}/{}({}){}".format(
            indent,
            self.__class__.__name__,
            self.token_type,
            super().__repr__(),
            '' jeżeli nie self.defects inaczej ' {}'.format(self.defects),
            )]

    def cte_encode(self, charset, policy):
        value = str(self)
        spróbuj:
            value.encode('us-ascii')
            zwróć value
        wyjąwszy UnicodeEncodeError:
            zwróć _ew.encode(value, charset)

    def pop_trailing_ws(self):
        # This terminates the recursion.
        zwróć Nic

    def pop_leading_fws(self):
        # This terminates the recursion.
        zwróć Nic

    @property
    def comments(self):
        zwróć []

    def has_leading_comment(self):
        zwróć Nieprawda

    def __getnewargs__(self):
        return(str(self), self.token_type)


klasa WhiteSpaceTerminal(Terminal):

    @property
    def value(self):
        zwróć ' '

    def startswith_fws(self):
        zwróć Prawda

    has_fws = Prawda


klasa ValueTerminal(Terminal):

    @property
    def value(self):
        zwróć self

    def startswith_fws(self):
        zwróć Nieprawda

    has_fws = Nieprawda

    def as_encoded_word(self, charset):
        zwróć _ew.encode(str(self), charset)


klasa EWWhiteSpaceTerminal(WhiteSpaceTerminal):

    @property
    def value(self):
        zwróć ''

    @property
    def encoded(self):
        zwróć self[:]

    def __str__(self):
        zwróć ''

    has_fws = Prawda


# XXX these need to become classes oraz used jako instances so
# that a program can't change them w a parse tree oraz screw
# up other parse trees.  Maybe should have  tests dla that, too.
DOT = ValueTerminal('.', 'dot')
ListSeparator = ValueTerminal(',', 'list-separator')
RouteComponentMarker = ValueTerminal('@', 'route-component-marker')

#
# Parser
#

# Parse strings according to RFC822/2047/2822/5322 rules.
#
# This jest a stateless parser.  Each get_XXX function accepts a string oraz
# returns either a Terminal albo a TokenList representing the RFC object named
# by the method oraz a string containing the remaining unparsed characters
# z the input.  Thus a parser method consumes the next syntactic construct
# of a given type oraz returns a token representing the construct plus the
# unparsed remainder of the input string.
#
# For example, jeżeli the first element of a structured header jest a 'phrase',
# then:
#
#     phrase, value = get_phrase(value)
#
# returns the complete phrase z the start of the string value, plus any
# characters left w the string after the phrase jest removed.

_wsp_splitter = re.compile(r'([{}]+)'.format(''.join(WSP))).split
_non_atom_end_matcher = re.compile(r"[^{}]+".format(
    ''.join(ATOM_ENDS).replace('\\','\\\\').replace(']','\]'))).match
_non_printable_finder = re.compile(r"[\x00-\x20\x7F]").findall
_non_token_end_matcher = re.compile(r"[^{}]+".format(
    ''.join(TOKEN_ENDS).replace('\\','\\\\').replace(']','\]'))).match
_non_attribute_end_matcher = re.compile(r"[^{}]+".format(
    ''.join(ATTRIBUTE_ENDS).replace('\\','\\\\').replace(']','\]'))).match
_non_extended_attribute_end_matcher = re.compile(r"[^{}]+".format(
    ''.join(EXTENDED_ATTRIBUTE_ENDS).replace(
                                    '\\','\\\\').replace(']','\]'))).match

def _validate_xtext(xtext):
    """If input token contains ASCII non-printables, register a defect."""

    non_printables = _non_printable_finder(xtext)
    jeżeli non_printables:
        xtext.defects.append(errors.NonPrintableDefect(non_printables))
    jeżeli utils._has_surrogates(xtext):
        xtext.defects.append(errors.UndecodableBytesDefect(
            "Non-ASCII characters found w header token"))

def _get_ptext_to_endchars(value, endchars):
    """Scan printables/quoted-pairs until endchars oraz zwróć unquoted ptext.

    This function turns a run of qcontent, ccontent-without-comments, albo
    dtext-with-quoted-printables into a single string by unquoting any
    quoted printables.  It returns the string, the remaining value, oraz
    a flag that jest Prawda iff there were any quoted printables decoded.

    """
    fragment, *remainder = _wsp_splitter(value, 1)
    vchars = []
    escape = Nieprawda
    had_qp = Nieprawda
    dla pos w range(len(fragment)):
        jeżeli fragment[pos] == '\\':
            jeżeli escape:
                escape = Nieprawda
                had_qp = Prawda
            inaczej:
                escape = Prawda
                kontynuuj
        jeżeli escape:
            escape = Nieprawda
        albo_inaczej fragment[pos] w endchars:
            przerwij
        vchars.append(fragment[pos])
    inaczej:
        pos = pos + 1
    zwróć ''.join(vchars), ''.join([fragment[pos:]] + remainder), had_qp

def get_fws(value):
    """FWS = 1*WSP

    This isn't the RFC definition.  We're using fws to represent tokens where
    folding can be done, but when we are parsing the *un*folding has already
    been done so we don't need to watch out dla CRLF.

    """
    newvalue = value.lstrip()
    fws = WhiteSpaceTerminal(value[:len(value)-len(newvalue)], 'fws')
    zwróć fws, newvalue

def get_encoded_word(value):
    """ encoded-word = "=?" charset "?" encoding "?" encoded-text "?="

    """
    ew = EncodedWord()
    jeżeli nie value.startswith('=?'):
        podnieś errors.HeaderParseError(
            "expected encoded word but found {}".format(value))
    tok, *remainder = value[2:].split('?=', 1)
    jeżeli tok == value[2:]:
        podnieś errors.HeaderParseError(
            "expected encoded word but found {}".format(value))
    remstr = ''.join(remainder)
    jeżeli len(remstr) > 1 oraz remstr[0] w hexdigits oraz remstr[1] w hexdigits:
        # The ? after the CTE was followed by an encoded word escape (=XX).
        rest, *remainder = remstr.split('?=', 1)
        tok = tok + '?=' + rest
    jeżeli len(tok.split()) > 1:
        ew.defects.append(errors.InvalidHeaderDefect(
            "whitespace inside encoded word"))
    ew.cte = value
    value = ''.join(remainder)
    spróbuj:
        text, charset, lang, defects = _ew.decode('=?' + tok + '?=')
    wyjąwszy ValueError:
        podnieś errors.HeaderParseError(
            "encoded word format invalid: '{}'".format(ew.cte))
    ew.charset = charset
    ew.lang = lang
    ew.defects.extend(defects)
    dopóki text:
        jeżeli text[0] w WSP:
            token, text = get_fws(text)
            ew.append(token)
            kontynuuj
        chars, *remainder = _wsp_splitter(text, 1)
        vtext = ValueTerminal(chars, 'vtext')
        _validate_xtext(vtext)
        ew.append(vtext)
        text = ''.join(remainder)
    zwróć ew, value

def get_unstructured(value):
    """unstructured = (*([FWS] vchar) *WSP) / obs-unstruct
       obs-unstruct = *((*LF *CR *(obs-utext) *LF *CR)) / FWS)
       obs-utext = %d0 / obs-NO-WS-CTL / LF / CR

       obs-NO-WS-CTL jest control characters wyjąwszy WSP/CR/LF.

    So, basically, we have printable runs, plus control characters albo nulls w
    the obsolete syntax, separated by whitespace.  Since RFC 2047 uses the
    obsolete syntax w its specification, but requires whitespace on either
    side of the encoded words, I can see no reason to need to separate the
    non-printable-non-whitespace z the printable runs jeżeli they occur, so we
    parse this into xtext tokens separated by WSP tokens.

    Because an 'unstructured' value must by definition constitute the entire
    value, this 'get' routine does nie zwróć a remaining value, only the
    parsed TokenList.

    """
    # XXX: but what about bare CR oraz LF?  They might signal the start albo
    # end of an encoded word.  YAGNI dla now, since our current parsers
    # will never send us strings przy bare CR albo LF.

    unstructured = UnstructuredTokenList()
    dopóki value:
        jeżeli value[0] w WSP:
            token, value = get_fws(value)
            unstructured.append(token)
            kontynuuj
        jeżeli value.startswith('=?'):
            spróbuj:
                token, value = get_encoded_word(value)
            wyjąwszy errors.HeaderParseError:
                # XXX: Need to figure out how to register defects when
                # appropriate here.
                dalej
            inaczej:
                have_ws = Prawda
                jeżeli len(unstructured) > 0:
                    jeżeli unstructured[-1].token_type != 'fws':
                        unstructured.defects.append(errors.InvalidHeaderDefect(
                            "missing whitespace before encoded word"))
                        have_ws = Nieprawda
                jeżeli have_ws oraz len(unstructured) > 1:
                    jeżeli unstructured[-2].token_type == 'encoded-word':
                        unstructured[-1] = EWWhiteSpaceTerminal(
                            unstructured[-1], 'fws')
                unstructured.append(token)
                kontynuuj
        tok, *remainder = _wsp_splitter(value, 1)
        vtext = ValueTerminal(tok, 'vtext')
        _validate_xtext(vtext)
        unstructured.append(vtext)
        value = ''.join(remainder)
    zwróć unstructured

def get_qp_ctext(value):
    """ctext = <printable ascii wyjąwszy \ ( )>

    This jest nie the RFC ctext, since we are handling nested comments w comment
    oraz unquoting quoted-pairs here.  We allow anything wyjąwszy the '()'
    characters, but jeżeli we find any ASCII other than the RFC defined printable
    ASCII an NonPrintableDefect jest added to the token's defects list.  Since
    quoted pairs are converted to their unquoted values, what jest returned jest
    a 'ptext' token.  In this case it jest a WhiteSpaceTerminal, so it's value
    jest ' '.

    """
    ptext, value, _ = _get_ptext_to_endchars(value, '()')
    ptext = WhiteSpaceTerminal(ptext, 'ptext')
    _validate_xtext(ptext)
    zwróć ptext, value

def get_qcontent(value):
    """qcontent = qtext / quoted-pair

    We allow anything wyjąwszy the DQUOTE character, but jeżeli we find any ASCII
    other than the RFC defined printable ASCII an NonPrintableDefect jest
    added to the token's defects list.  Any quoted pairs are converted to their
    unquoted values, so what jest returned jest a 'ptext' token.  In this case it
    jest a ValueTerminal.

    """
    ptext, value, _ = _get_ptext_to_endchars(value, '"')
    ptext = ValueTerminal(ptext, 'ptext')
    _validate_xtext(ptext)
    zwróć ptext, value

def get_atext(value):
    """atext = <matches _atext_matcher>

    We allow any non-ATOM_ENDS w atext, but add an InvalidATextDefect to
    the token's defects list jeżeli we find non-atext characters.
    """
    m = _non_atom_end_matcher(value)
    jeżeli nie m:
        podnieś errors.HeaderParseError(
            "expected atext but found '{}'".format(value))
    atext = m.group()
    value = value[len(atext):]
    atext = ValueTerminal(atext, 'atext')
    _validate_xtext(atext)
    zwróć atext, value

def get_bare_quoted_string(value):
    """bare-quoted-string = DQUOTE *([FWS] qcontent) [FWS] DQUOTE

    A quoted-string without the leading albo trailing white space.  Its
    value jest the text between the quote marks, przy whitespace
    preserved oraz quoted pairs decoded.
    """
    jeżeli value[0] != '"':
        podnieś errors.HeaderParseError(
            "expected '\"' but found '{}'".format(value))
    bare_quoted_string = BareQuotedString()
    value = value[1:]
    dopóki value oraz value[0] != '"':
        jeżeli value[0] w WSP:
            token, value = get_fws(value)
        albo_inaczej value[:2] == '=?':
            spróbuj:
                token, value = get_encoded_word(value)
                bare_quoted_string.defects.append(errors.InvalidHeaderDefect(
                    "encoded word inside quoted string"))
            wyjąwszy errors.HeaderParseError:
                token, value = get_qcontent(value)
        inaczej:
            token, value = get_qcontent(value)
        bare_quoted_string.append(token)
    jeżeli nie value:
        bare_quoted_string.defects.append(errors.InvalidHeaderDefect(
            "end of header inside quoted string"))
        zwróć bare_quoted_string, value
    zwróć bare_quoted_string, value[1:]

def get_comment(value):
    """comment = "(" *([FWS] ccontent) [FWS] ")"
       ccontent = ctext / quoted-pair / comment

    We handle nested comments here, oraz quoted-pair w our qp-ctext routine.
    """
    jeżeli value oraz value[0] != '(':
        podnieś errors.HeaderParseError(
            "expected '(' but found '{}'".format(value))
    comment = Comment()
    value = value[1:]
    dopóki value oraz value[0] != ")":
        jeżeli value[0] w WSP:
            token, value = get_fws(value)
        albo_inaczej value[0] == '(':
            token, value = get_comment(value)
        inaczej:
            token, value = get_qp_ctext(value)
        comment.append(token)
    jeżeli nie value:
        comment.defects.append(errors.InvalidHeaderDefect(
            "end of header inside comment"))
        zwróć comment, value
    zwróć comment, value[1:]

def get_cfws(value):
    """CFWS = (1*([FWS] comment) [FWS]) / FWS

    """
    cfws = CFWSList()
    dopóki value oraz value[0] w CFWS_LEADER:
        jeżeli value[0] w WSP:
            token, value = get_fws(value)
        inaczej:
            token, value = get_comment(value)
        cfws.append(token)
    zwróć cfws, value

def get_quoted_string(value):
    """quoted-string = [CFWS] <bare-quoted-string> [CFWS]

    'bare-quoted-string' jest an intermediate klasa defined by this
    parser oraz nie by the RFC grammar.  It jest the quoted string
    without any attached CFWS.
    """
    quoted_string = QuotedString()
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        quoted_string.append(token)
    token, value = get_bare_quoted_string(value)
    quoted_string.append(token)
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        quoted_string.append(token)
    zwróć quoted_string, value

def get_atom(value):
    """atom = [CFWS] 1*atext [CFWS]

    An atom could be an rfc2047 encoded word.
    """
    atom = Atom()
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        atom.append(token)
    jeżeli value oraz value[0] w ATOM_ENDS:
        podnieś errors.HeaderParseError(
            "expected atom but found '{}'".format(value))
    jeżeli value.startswith('=?'):
        spróbuj:
            token, value = get_encoded_word(value)
        wyjąwszy errors.HeaderParseError:
            # XXX: need to figure out how to register defects when
            # appropriate here.
            token, value = get_atext(value)
    inaczej:
        token, value = get_atext(value)
    atom.append(token)
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        atom.append(token)
    zwróć atom, value

def get_dot_atom_text(value):
    """ dot-text = 1*atext *("." 1*atext)

    """
    dot_atom_text = DotAtomText()
    jeżeli nie value albo value[0] w ATOM_ENDS:
        podnieś errors.HeaderParseError("expected atom at a start of "
            "dot-atom-text but found '{}'".format(value))
    dopóki value oraz value[0] nie w ATOM_ENDS:
        token, value = get_atext(value)
        dot_atom_text.append(token)
        jeżeli value oraz value[0] == '.':
            dot_atom_text.append(DOT)
            value = value[1:]
    jeżeli dot_atom_text[-1] jest DOT:
        podnieś errors.HeaderParseError("expected atom at end of dot-atom-text "
            "but found '{}'".format('.'+value))
    zwróć dot_atom_text, value

def get_dot_atom(value):
    """ dot-atom = [CFWS] dot-atom-text [CFWS]

    Any place we can have a dot atom, we could instead have an rfc2047 encoded
    word.
    """
    dot_atom = DotAtom()
    jeżeli value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        dot_atom.append(token)
    jeżeli value.startswith('=?'):
        spróbuj:
            token, value = get_encoded_word(value)
        wyjąwszy errors.HeaderParseError:
            # XXX: need to figure out how to register defects when
            # appropriate here.
            token, value = get_dot_atom_text(value)
    inaczej:
        token, value = get_dot_atom_text(value)
    dot_atom.append(token)
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        dot_atom.append(token)
    zwróć dot_atom, value

def get_word(value):
    """word = atom / quoted-string

    Either atom albo quoted-string may start przy CFWS.  We have to peel off this
    CFWS first to determine which type of word to parse.  Afterward we splice
    the leading CFWS, jeżeli any, into the parsed sub-token.

    If neither an atom albo a quoted-string jest found before the next special, a
    HeaderParseError jest podnieśd.

    The token returned jest either an Atom albo a QuotedString, jako appropriate.
    This means the 'word' level of the formal grammar jest nie represented w the
    parse tree; this jest because having that extra layer when manipulating the
    parse tree jest more confusing than it jest helpful.

    """
    jeżeli value[0] w CFWS_LEADER:
        leader, value = get_cfws(value)
    inaczej:
        leader = Nic
    jeżeli value[0]=='"':
        token, value = get_quoted_string(value)
    albo_inaczej value[0] w SPECIALS:
        podnieś errors.HeaderParseError("Expected 'atom' albo 'quoted-string' "
                                      "but found '{}'".format(value))
    inaczej:
        token, value = get_atom(value)
    jeżeli leader jest nie Nic:
        token[:0] = [leader]
    zwróć token, value

def get_phrase(value):
    """ phrase = 1*word / obs-phrase
        obs-phrase = word *(word / "." / CFWS)

    This means a phrase can be a sequence of words, periods, oraz CFWS w any
    order jako long jako it starts przy at least one word.  If anything other than
    words jest detected, an ObsoleteHeaderDefect jest added to the token's defect
    list.  We also accept a phrase that starts przy CFWS followed by a dot;
    this jest registered jako an InvalidHeaderDefect, since it jest nie supported by
    even the obsolete grammar.

    """
    phrase = Phrase()
    spróbuj:
        token, value = get_word(value)
        phrase.append(token)
    wyjąwszy errors.HeaderParseError:
        phrase.defects.append(errors.InvalidHeaderDefect(
            "phrase does nie start przy word"))
    dopóki value oraz value[0] nie w PHRASE_ENDS:
        jeżeli value[0]=='.':
            phrase.append(DOT)
            phrase.defects.append(errors.ObsoleteHeaderDefect(
                "period w 'phrase'"))
            value = value[1:]
        inaczej:
            spróbuj:
                token, value = get_word(value)
            wyjąwszy errors.HeaderParseError:
                jeżeli value[0] w CFWS_LEADER:
                    token, value = get_cfws(value)
                    phrase.defects.append(errors.ObsoleteHeaderDefect(
                        "comment found without atom"))
                inaczej:
                    podnieś
            phrase.append(token)
    zwróć phrase, value

def get_local_part(value):
    """ local-part = dot-atom / quoted-string / obs-local-part

    """
    local_part = LocalPart()
    leader = Nic
    jeżeli value[0] w CFWS_LEADER:
        leader, value = get_cfws(value)
    jeżeli nie value:
        podnieś errors.HeaderParseError(
            "expected local-part but found '{}'".format(value))
    spróbuj:
        token, value = get_dot_atom(value)
    wyjąwszy errors.HeaderParseError:
        spróbuj:
            token, value = get_word(value)
        wyjąwszy errors.HeaderParseError:
            jeżeli value[0] != '\\' oraz value[0] w PHRASE_ENDS:
                podnieś
            token = TokenList()
    jeżeli leader jest nie Nic:
        token[:0] = [leader]
    local_part.append(token)
    jeżeli value oraz (value[0]=='\\' albo value[0] nie w PHRASE_ENDS):
        obs_local_part, value = get_obs_local_part(str(local_part) + value)
        jeżeli obs_local_part.token_type == 'invalid-obs-local-part':
            local_part.defects.append(errors.InvalidHeaderDefect(
                "local-part jest nie dot-atom, quoted-string, albo obs-local-part"))
        inaczej:
            local_part.defects.append(errors.ObsoleteHeaderDefect(
                "local-part jest nie a dot-atom (contains CFWS)"))
        local_part[0] = obs_local_part
    spróbuj:
        local_part.value.encode('ascii')
    wyjąwszy UnicodeEncodeError:
        local_part.defects.append(errors.NonASCIILocalPartDefect(
                "local-part contains non-ASCII characters)"))
    zwróć local_part, value

def get_obs_local_part(value):
    """ obs-local-part = word *("." word)
    """
    obs_local_part = ObsLocalPart()
    last_non_ws_was_dot = Nieprawda
    dopóki value oraz (value[0]=='\\' albo value[0] nie w PHRASE_ENDS):
        jeżeli value[0] == '.':
            jeżeli last_non_ws_was_dot:
                obs_local_part.defects.append(errors.InvalidHeaderDefect(
                    "invalid repeated '.'"))
            obs_local_part.append(DOT)
            last_non_ws_was_dot = Prawda
            value = value[1:]
            kontynuuj
        albo_inaczej value[0]=='\\':
            obs_local_part.append(ValueTerminal(value[0],
                                                'misplaced-special'))
            value = value[1:]
            obs_local_part.defects.append(errors.InvalidHeaderDefect(
                "'\\' character outside of quoted-string/ccontent"))
            last_non_ws_was_dot = Nieprawda
            kontynuuj
        jeżeli obs_local_part oraz obs_local_part[-1].token_type != 'dot':
            obs_local_part.defects.append(errors.InvalidHeaderDefect(
                "missing '.' between words"))
        spróbuj:
            token, value = get_word(value)
            last_non_ws_was_dot = Nieprawda
        wyjąwszy errors.HeaderParseError:
            jeżeli value[0] nie w CFWS_LEADER:
                podnieś
            token, value = get_cfws(value)
        obs_local_part.append(token)
    jeżeli (obs_local_part[0].token_type == 'dot' albo
            obs_local_part[0].token_type=='cfws' oraz
            obs_local_part[1].token_type=='dot'):
        obs_local_part.defects.append(errors.InvalidHeaderDefect(
            "Invalid leading '.' w local part"))
    jeżeli (obs_local_part[-1].token_type == 'dot' albo
            obs_local_part[-1].token_type=='cfws' oraz
            obs_local_part[-2].token_type=='dot'):
        obs_local_part.defects.append(errors.InvalidHeaderDefect(
            "Invalid trailing '.' w local part"))
    jeżeli obs_local_part.defects:
        obs_local_part.token_type = 'invalid-obs-local-part'
    zwróć obs_local_part, value

def get_dtext(value):
    """ dtext = <printable ascii wyjąwszy \ [ ]> / obs-dtext
        obs-dtext = obs-NO-WS-CTL / quoted-pair

    We allow anything wyjąwszy the excluded characters, but jeżeli we find any
    ASCII other than the RFC defined printable ASCII an NonPrintableDefect jest
    added to the token's defects list.  Quoted pairs are converted to their
    unquoted values, so what jest returned jest a ptext token, w this case a
    ValueTerminal.  If there were quoted-printables, an ObsoleteHeaderDefect jest
    added to the returned token's defect list.

    """
    ptext, value, had_qp = _get_ptext_to_endchars(value, '[]')
    ptext = ValueTerminal(ptext, 'ptext')
    jeżeli had_qp:
        ptext.defects.append(errors.ObsoleteHeaderDefect(
            "quoted printable found w domain-literal"))
    _validate_xtext(ptext)
    zwróć ptext, value

def _check_for_early_dl_end(value, domain_literal):
    jeżeli value:
        zwróć Nieprawda
    domain_literal.append(errors.InvalidHeaderDefect(
        "end of input inside domain-literal"))
    domain_literal.append(ValueTerminal(']', 'domain-literal-end'))
    zwróć Prawda

def get_domain_literal(value):
    """ domain-literal = [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]

    """
    domain_literal = DomainLiteral()
    jeżeli value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        domain_literal.append(token)
    jeżeli nie value:
        podnieś errors.HeaderParseError("expected domain-literal")
    jeżeli value[0] != '[':
        podnieś errors.HeaderParseError("expected '[' at start of domain-literal "
                "but found '{}'".format(value))
    value = value[1:]
    jeżeli _check_for_early_dl_end(value, domain_literal):
        zwróć domain_literal, value
    domain_literal.append(ValueTerminal('[', 'domain-literal-start'))
    jeżeli value[0] w WSP:
        token, value = get_fws(value)
        domain_literal.append(token)
    token, value = get_dtext(value)
    domain_literal.append(token)
    jeżeli _check_for_early_dl_end(value, domain_literal):
        zwróć domain_literal, value
    jeżeli value[0] w WSP:
        token, value = get_fws(value)
        domain_literal.append(token)
    jeżeli _check_for_early_dl_end(value, domain_literal):
        zwróć domain_literal, value
    jeżeli value[0] != ']':
        podnieś errors.HeaderParseError("expected ']' at end of domain-literal "
                "but found '{}'".format(value))
    domain_literal.append(ValueTerminal(']', 'domain-literal-end'))
    value = value[1:]
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        domain_literal.append(token)
    zwróć domain_literal, value

def get_domain(value):
    """ domain = dot-atom / domain-literal / obs-domain
        obs-domain = atom *("." atom))

    """
    domain = Domain()
    leader = Nic
    jeżeli value[0] w CFWS_LEADER:
        leader, value = get_cfws(value)
    jeżeli nie value:
        podnieś errors.HeaderParseError(
            "expected domain but found '{}'".format(value))
    jeżeli value[0] == '[':
        token, value = get_domain_literal(value)
        jeżeli leader jest nie Nic:
            token[:0] = [leader]
        domain.append(token)
        zwróć domain, value
    spróbuj:
        token, value = get_dot_atom(value)
    wyjąwszy errors.HeaderParseError:
        token, value = get_atom(value)
    jeżeli leader jest nie Nic:
        token[:0] = [leader]
    domain.append(token)
    jeżeli value oraz value[0] == '.':
        domain.defects.append(errors.ObsoleteHeaderDefect(
            "domain jest nie a dot-atom (contains CFWS)"))
        jeżeli domain[0].token_type == 'dot-atom':
            domain[:] = domain[0]
        dopóki value oraz value[0] == '.':
            domain.append(DOT)
            token, value = get_atom(value[1:])
            domain.append(token)
    zwróć domain, value

def get_addr_spec(value):
    """ addr-spec = local-part "@" domain

    """
    addr_spec = AddrSpec()
    token, value = get_local_part(value)
    addr_spec.append(token)
    jeżeli nie value albo value[0] != '@':
        addr_spec.defects.append(errors.InvalidHeaderDefect(
            "add-spec local part przy no domain"))
        zwróć addr_spec, value
    addr_spec.append(ValueTerminal('@', 'address-at-symbol'))
    token, value = get_domain(value[1:])
    addr_spec.append(token)
    zwróć addr_spec, value

def get_obs_route(value):
    """ obs-route = obs-domain-list ":"
        obs-domain-list = *(CFWS / ",") "@" domain *("," [CFWS] ["@" domain])

        Returns an obs-route token przy the appropriate sub-tokens (that is,
        there jest no obs-domain-list w the parse tree).
    """
    obs_route = ObsRoute()
    dopóki value oraz (value[0]==',' albo value[0] w CFWS_LEADER):
        jeżeli value[0] w CFWS_LEADER:
            token, value = get_cfws(value)
            obs_route.append(token)
        albo_inaczej value[0] == ',':
            obs_route.append(ListSeparator)
            value = value[1:]
    jeżeli nie value albo value[0] != '@':
        podnieś errors.HeaderParseError(
            "expected obs-route domain but found '{}'".format(value))
    obs_route.append(RouteComponentMarker)
    token, value = get_domain(value[1:])
    obs_route.append(token)
    dopóki value oraz value[0]==',':
        obs_route.append(ListSeparator)
        value = value[1:]
        jeżeli nie value:
            przerwij
        jeżeli value[0] w CFWS_LEADER:
            token, value = get_cfws(value)
            obs_route.append(token)
        jeżeli value[0] == '@':
            obs_route.append(RouteComponentMarker)
            token, value = get_domain(value[1:])
            obs_route.append(token)
    jeżeli nie value:
        podnieś errors.HeaderParseError("end of header dopóki parsing obs-route")
    jeżeli value[0] != ':':
        podnieś errors.HeaderParseError( "expected ':' marking end of "
            "obs-route but found '{}'".format(value))
    obs_route.append(ValueTerminal(':', 'end-of-obs-route-marker'))
    zwróć obs_route, value[1:]

def get_angle_addr(value):
    """ angle-addr = [CFWS] "<" addr-spec ">" [CFWS] / obs-angle-addr
        obs-angle-addr = [CFWS] "<" obs-route addr-spec ">" [CFWS]

    """
    angle_addr = AngleAddr()
    jeżeli value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        angle_addr.append(token)
    jeżeli nie value albo value[0] != '<':
        podnieś errors.HeaderParseError(
            "expected angle-addr but found '{}'".format(value))
    angle_addr.append(ValueTerminal('<', 'angle-addr-start'))
    value = value[1:]
    # Although it jest nie legal per RFC5322, SMTP uses '<>' w certain
    # circumstances.
    jeżeli value[0] == '>':
        angle_addr.append(ValueTerminal('>', 'angle-addr-end'))
        angle_addr.defects.append(errors.InvalidHeaderDefect(
            "null addr-spec w angle-addr"))
        value = value[1:]
        zwróć angle_addr, value
    spróbuj:
        token, value = get_addr_spec(value)
    wyjąwszy errors.HeaderParseError:
        spróbuj:
            token, value = get_obs_route(value)
            angle_addr.defects.append(errors.ObsoleteHeaderDefect(
                "obsolete route specification w angle-addr"))
        wyjąwszy errors.HeaderParseError:
            podnieś errors.HeaderParseError(
                "expected addr-spec albo obs-route but found '{}'".format(value))
        angle_addr.append(token)
        token, value = get_addr_spec(value)
    angle_addr.append(token)
    jeżeli value oraz value[0] == '>':
        value = value[1:]
    inaczej:
        angle_addr.defects.append(errors.InvalidHeaderDefect(
            "missing trailing '>' on angle-addr"))
    angle_addr.append(ValueTerminal('>', 'angle-addr-end'))
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        angle_addr.append(token)
    zwróć angle_addr, value

def get_display_name(value):
    """ display-name = phrase

    Because this jest simply a name-rule, we don't zwróć a display-name
    token containing a phrase, but rather a display-name token with
    the content of the phrase.

    """
    display_name = DisplayName()
    token, value = get_phrase(value)
    display_name.extend(token[:])
    display_name.defects = token.defects[:]
    zwróć display_name, value


def get_name_addr(value):
    """ name-addr = [display-name] angle-addr

    """
    name_addr = NameAddr()
    # Both the optional display name oraz the angle-addr can start przy cfws.
    leader = Nic
    jeżeli value[0] w CFWS_LEADER:
        leader, value = get_cfws(value)
        jeżeli nie value:
            podnieś errors.HeaderParseError(
                "expected name-addr but found '{}'".format(leader))
    jeżeli value[0] != '<':
        jeżeli value[0] w PHRASE_ENDS:
            podnieś errors.HeaderParseError(
                "expected name-addr but found '{}'".format(value))
        token, value = get_display_name(value)
        jeżeli nie value:
            podnieś errors.HeaderParseError(
                "expected name-addr but found '{}'".format(token))
        jeżeli leader jest nie Nic:
            token[0][:0] = [leader]
            leader = Nic
        name_addr.append(token)
    token, value = get_angle_addr(value)
    jeżeli leader jest nie Nic:
        token[:0] = [leader]
    name_addr.append(token)
    zwróć name_addr, value

def get_mailbox(value):
    """ mailbox = name-addr / addr-spec

    """
    # The only way to figure out jeżeli we are dealing przy a name-addr albo an
    # addr-spec jest to try parsing each one.
    mailbox = Mailbox()
    spróbuj:
        token, value = get_name_addr(value)
    wyjąwszy errors.HeaderParseError:
        spróbuj:
            token, value = get_addr_spec(value)
        wyjąwszy errors.HeaderParseError:
            podnieś errors.HeaderParseError(
                "expected mailbox but found '{}'".format(value))
    jeżeli any(isinstance(x, errors.InvalidHeaderDefect)
                       dla x w token.all_defects):
        mailbox.token_type = 'invalid-mailbox'
    mailbox.append(token)
    zwróć mailbox, value

def get_invalid_mailbox(value, endchars):
    """ Read everything up to one of the chars w endchars.

    This jest outside the formal grammar.  The InvalidMailbox TokenList that jest
    returned acts like a Mailbox, but the data attributes are Nic.

    """
    invalid_mailbox = InvalidMailbox()
    dopóki value oraz value[0] nie w endchars:
        jeżeli value[0] w PHRASE_ENDS:
            invalid_mailbox.append(ValueTerminal(value[0],
                                                 'misplaced-special'))
            value = value[1:]
        inaczej:
            token, value = get_phrase(value)
            invalid_mailbox.append(token)
    zwróć invalid_mailbox, value

def get_mailbox_list(value):
    """ mailbox-list = (mailbox *("," mailbox)) / obs-mbox-list
        obs-mbox-list = *([CFWS] ",") mailbox *("," [mailbox / CFWS])

    For this routine we go outside the formal grammar w order to improve error
    handling.  We recognize the end of the mailbox list only at the end of the
    value albo at a ';' (the group terminator).  This jest so that we can turn
    invalid mailboxes into InvalidMailbox tokens oraz continue parsing any
    remaining valid mailboxes.  We also allow all mailbox entries to be null,
    oraz this condition jest handled appropriately at a higher level.

    """
    mailbox_list = MailboxList()
    dopóki value oraz value[0] != ';':
        spróbuj:
            token, value = get_mailbox(value)
            mailbox_list.append(token)
        wyjąwszy errors.HeaderParseError:
            leader = Nic
            jeżeli value[0] w CFWS_LEADER:
                leader, value = get_cfws(value)
                jeżeli nie value albo value[0] w ',;':
                    mailbox_list.append(leader)
                    mailbox_list.defects.append(errors.ObsoleteHeaderDefect(
                        "empty element w mailbox-list"))
                inaczej:
                    token, value = get_invalid_mailbox(value, ',;')
                    jeżeli leader jest nie Nic:
                        token[:0] = [leader]
                    mailbox_list.append(token)
                    mailbox_list.defects.append(errors.InvalidHeaderDefect(
                        "invalid mailbox w mailbox-list"))
            albo_inaczej value[0] == ',':
                mailbox_list.defects.append(errors.ObsoleteHeaderDefect(
                    "empty element w mailbox-list"))
            inaczej:
                token, value = get_invalid_mailbox(value, ',;')
                jeżeli leader jest nie Nic:
                    token[:0] = [leader]
                mailbox_list.append(token)
                mailbox_list.defects.append(errors.InvalidHeaderDefect(
                    "invalid mailbox w mailbox-list"))
        jeżeli value oraz value[0] nie w ',;':
            # Crap after mailbox; treat it jako an invalid mailbox.
            # The mailbox info will still be available.
            mailbox = mailbox_list[-1]
            mailbox.token_type = 'invalid-mailbox'
            token, value = get_invalid_mailbox(value, ',;')
            mailbox.extend(token)
            mailbox_list.defects.append(errors.InvalidHeaderDefect(
                "invalid mailbox w mailbox-list"))
        jeżeli value oraz value[0] == ',':
            mailbox_list.append(ListSeparator)
            value = value[1:]
    zwróć mailbox_list, value


def get_group_list(value):
    """ group-list = mailbox-list / CFWS / obs-group-list
        obs-group-list = 1*([CFWS] ",") [CFWS]

    """
    group_list = GroupList()
    jeżeli nie value:
        group_list.defects.append(errors.InvalidHeaderDefect(
            "end of header before group-list"))
        zwróć group_list, value
    leader = Nic
    jeżeli value oraz value[0] w CFWS_LEADER:
        leader, value = get_cfws(value)
        jeżeli nie value:
            # This should never happen w email parsing, since CFWS-only jest a
            # legal alternative to group-list w a group, which jest the only
            # place group-list appears.
            group_list.defects.append(errors.InvalidHeaderDefect(
                "end of header w group-list"))
            group_list.append(leader)
            zwróć group_list, value
        jeżeli value[0] == ';':
            group_list.append(leader)
            zwróć group_list, value
    token, value = get_mailbox_list(value)
    jeżeli len(token.all_mailboxes)==0:
        jeżeli leader jest nie Nic:
            group_list.append(leader)
        group_list.extend(token)
        group_list.defects.append(errors.ObsoleteHeaderDefect(
            "group-list przy empty entries"))
        zwróć group_list, value
    jeżeli leader jest nie Nic:
        token[:0] = [leader]
    group_list.append(token)
    zwróć group_list, value

def get_group(value):
    """ group = display-name ":" [group-list] ";" [CFWS]

    """
    group = Group()
    token, value = get_display_name(value)
    jeżeli nie value albo value[0] != ':':
        podnieś errors.HeaderParseError("expected ':' at end of group "
            "display name but found '{}'".format(value))
    group.append(token)
    group.append(ValueTerminal(':', 'group-display-name-terminator'))
    value = value[1:]
    jeżeli value oraz value[0] == ';':
        group.append(ValueTerminal(';', 'group-terminator'))
        zwróć group, value[1:]
    token, value = get_group_list(value)
    group.append(token)
    jeżeli nie value:
        group.defects.append(errors.InvalidHeaderDefect(
            "end of header w group"))
    jeżeli value[0] != ';':
        podnieś errors.HeaderParseError(
            "expected ';' at end of group but found {}".format(value))
    group.append(ValueTerminal(';', 'group-terminator'))
    value = value[1:]
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        group.append(token)
    zwróć group, value

def get_address(value):
    """ address = mailbox / group

    Note that counter-intuitively, an address can be either a single address albo
    a list of addresses (a group).  This jest why the returned Address object has
    a 'mailboxes' attribute which treats a single address jako a list of length
    one.  When you need to differentiate between to two cases, extract the single
    element, which jest either a mailbox albo a group token.

    """
    # The formal grammar isn't very helpful when parsing an address.  mailbox
    # oraz group, especially when allowing dla obsolete forms, start off very
    # similarly.  It jest only when you reach one of @, <, albo : that you know
    # what you've got.  So, we try each one w turn, starting przy the more
    # likely of the two.  We could perhaps make this more efficient by looking
    # dla a phrase oraz then branching based on the next character, but that
    # would be a premature optimization.
    address = Address()
    spróbuj:
        token, value = get_group(value)
    wyjąwszy errors.HeaderParseError:
        spróbuj:
            token, value = get_mailbox(value)
        wyjąwszy errors.HeaderParseError:
            podnieś errors.HeaderParseError(
                "expected address but found '{}'".format(value))
    address.append(token)
    zwróć address, value

def get_address_list(value):
    """ address_list = (address *("," address)) / obs-addr-list
        obs-addr-list = *([CFWS] ",") address *("," [address / CFWS])

    We depart z the formal grammar here by continuing to parse until the end
    of the input, assuming the input to be entirely composed of an
    address-list.  This jest always true w email parsing, oraz allows us
    to skip invalid addresses to parse additional valid ones.

    """
    address_list = AddressList()
    dopóki value:
        spróbuj:
            token, value = get_address(value)
            address_list.append(token)
        wyjąwszy errors.HeaderParseError jako err:
            leader = Nic
            jeżeli value[0] w CFWS_LEADER:
                leader, value = get_cfws(value)
                jeżeli nie value albo value[0] == ',':
                    address_list.append(leader)
                    address_list.defects.append(errors.ObsoleteHeaderDefect(
                        "address-list entry przy no content"))
                inaczej:
                    token, value = get_invalid_mailbox(value, ',')
                    jeżeli leader jest nie Nic:
                        token[:0] = [leader]
                    address_list.append(Address([token]))
                    address_list.defects.append(errors.InvalidHeaderDefect(
                        "invalid address w address-list"))
            albo_inaczej value[0] == ',':
                address_list.defects.append(errors.ObsoleteHeaderDefect(
                    "empty element w address-list"))
            inaczej:
                token, value = get_invalid_mailbox(value, ',')
                jeżeli leader jest nie Nic:
                    token[:0] = [leader]
                address_list.append(Address([token]))
                address_list.defects.append(errors.InvalidHeaderDefect(
                    "invalid address w address-list"))
        jeżeli value oraz value[0] != ',':
            # Crap after address; treat it jako an invalid mailbox.
            # The mailbox info will still be available.
            mailbox = address_list[-1][0]
            mailbox.token_type = 'invalid-mailbox'
            token, value = get_invalid_mailbox(value, ',')
            mailbox.extend(token)
            address_list.defects.append(errors.InvalidHeaderDefect(
                "invalid address w address-list"))
        jeżeli value:  # Must be a , at this point.
            address_list.append(ValueTerminal(',', 'list-separator'))
            value = value[1:]
    zwróć address_list, value

#
# XXX: As I begin to add additional header parsers, I'm realizing we probably
# have two level of parser routines: the get_XXX methods that get a token w
# the grammar, oraz parse_XXX methods that parse an entire field value.  So
# get_address_list above should really be a parse_ method, jako probably should
# be get_unstructured.
#

def parse_mime_version(value):
    """ mime-version = [CFWS] 1*digit [CFWS] "." [CFWS] 1*digit [CFWS]

    """
    # The [CFWS] jest implicit w the RFC 2045 BNF.
    # XXX: This routine jest a bit verbose, should factor out a get_int method.
    mime_version = MIMEVersion()
    jeżeli nie value:
        mime_version.defects.append(errors.HeaderMissingRequiredValue(
            "Missing MIME version number (eg: 1.0)"))
        zwróć mime_version
    jeżeli value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
        jeżeli nie value:
            mime_version.defects.append(errors.HeaderMissingRequiredValue(
                "Expected MIME version number but found only CFWS"))
    digits = ''
    dopóki value oraz value[0] != '.' oraz value[0] nie w CFWS_LEADER:
        digits += value[0]
        value = value[1:]
    jeżeli nie digits.isdigit():
        mime_version.defects.append(errors.InvalidHeaderDefect(
            "Expected MIME major version number but found {!r}".format(digits)))
        mime_version.append(ValueTerminal(digits, 'xtext'))
    inaczej:
        mime_version.major = int(digits)
        mime_version.append(ValueTerminal(digits, 'digits'))
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
    jeżeli nie value albo value[0] != '.':
        jeżeli mime_version.major jest nie Nic:
            mime_version.defects.append(errors.InvalidHeaderDefect(
                "Incomplete MIME version; found only major number"))
        jeżeli value:
            mime_version.append(ValueTerminal(value, 'xtext'))
        zwróć mime_version
    mime_version.append(ValueTerminal('.', 'version-separator'))
    value = value[1:]
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
    jeżeli nie value:
        jeżeli mime_version.major jest nie Nic:
            mime_version.defects.append(errors.InvalidHeaderDefect(
                "Incomplete MIME version; found only major number"))
        zwróć mime_version
    digits = ''
    dopóki value oraz value[0] nie w CFWS_LEADER:
        digits += value[0]
        value = value[1:]
    jeżeli nie digits.isdigit():
        mime_version.defects.append(errors.InvalidHeaderDefect(
            "Expected MIME minor version number but found {!r}".format(digits)))
        mime_version.append(ValueTerminal(digits, 'xtext'))
    inaczej:
        mime_version.minor = int(digits)
        mime_version.append(ValueTerminal(digits, 'digits'))
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
    jeżeli value:
        mime_version.defects.append(errors.InvalidHeaderDefect(
            "Excess non-CFWS text after MIME version"))
        mime_version.append(ValueTerminal(value, 'xtext'))
    zwróć mime_version

def get_invalid_parameter(value):
    """ Read everything up to the next ';'.

    This jest outside the formal grammar.  The InvalidParameter TokenList that jest
    returned acts like a Parameter, but the data attributes are Nic.

    """
    invalid_parameter = InvalidParameter()
    dopóki value oraz value[0] != ';':
        jeżeli value[0] w PHRASE_ENDS:
            invalid_parameter.append(ValueTerminal(value[0],
                                                   'misplaced-special'))
            value = value[1:]
        inaczej:
            token, value = get_phrase(value)
            invalid_parameter.append(token)
    zwróć invalid_parameter, value

def get_ttext(value):
    """ttext = <matches _ttext_matcher>

    We allow any non-TOKEN_ENDS w ttext, but add defects to the token's
    defects list jeżeli we find non-ttext characters.  We also register defects for
    *any* non-printables even though the RFC doesn't exclude all of them,
    because we follow the spirit of RFC 5322.

    """
    m = _non_token_end_matcher(value)
    jeżeli nie m:
        podnieś errors.HeaderParseError(
            "expected ttext but found '{}'".format(value))
    ttext = m.group()
    value = value[len(ttext):]
    ttext = ValueTerminal(ttext, 'ttext')
    _validate_xtext(ttext)
    zwróć ttext, value

def get_token(value):
    """token = [CFWS] 1*ttext [CFWS]

    The RFC equivalent of ttext jest any US-ASCII chars wyjąwszy space, ctls, albo
    tspecials.  We also exclude tabs even though the RFC doesn't.

    The RFC implies the CFWS but jest nie explicit about it w the BNF.

    """
    mtoken = Token()
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        mtoken.append(token)
    jeżeli value oraz value[0] w TOKEN_ENDS:
        podnieś errors.HeaderParseError(
            "expected token but found '{}'".format(value))
    token, value = get_ttext(value)
    mtoken.append(token)
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        mtoken.append(token)
    zwróć mtoken, value

def get_attrtext(value):
    """attrtext = 1*(any non-ATTRIBUTE_ENDS character)

    We allow any non-ATTRIBUTE_ENDS w attrtext, but add defects to the
    token's defects list jeżeli we find non-attrtext characters.  We also register
    defects dla *any* non-printables even though the RFC doesn't exclude all of
    them, because we follow the spirit of RFC 5322.

    """
    m = _non_attribute_end_matcher(value)
    jeżeli nie m:
        podnieś errors.HeaderParseError(
            "expected attrtext but found {!r}".format(value))
    attrtext = m.group()
    value = value[len(attrtext):]
    attrtext = ValueTerminal(attrtext, 'attrtext')
    _validate_xtext(attrtext)
    zwróć attrtext, value

def get_attribute(value):
    """ [CFWS] 1*attrtext [CFWS]

    This version of the BNF makes the CFWS explicit, oraz jako usual we use a
    value terminal dla the actual run of characters.  The RFC equivalent of
    attrtext jest the token characters, przy the subtraction of '*', "'", oraz '%'.
    We include tab w the excluded set just jako we do dla token.

    """
    attribute = Attribute()
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    jeżeli value oraz value[0] w ATTRIBUTE_ENDS:
        podnieś errors.HeaderParseError(
            "expected token but found '{}'".format(value))
    token, value = get_attrtext(value)
    attribute.append(token)
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    zwróć attribute, value

def get_extended_attrtext(value):
    """attrtext = 1*(any non-ATTRIBUTE_ENDS character plus '%')

    This jest a special parsing routine so that we get a value that
    includes % escapes jako a single string (which we decode jako a single
    string later).

    """
    m = _non_extended_attribute_end_matcher(value)
    jeżeli nie m:
        podnieś errors.HeaderParseError(
            "expected extended attrtext but found {!r}".format(value))
    attrtext = m.group()
    value = value[len(attrtext):]
    attrtext = ValueTerminal(attrtext, 'extended-attrtext')
    _validate_xtext(attrtext)
    zwróć attrtext, value

def get_extended_attribute(value):
    """ [CFWS] 1*extended_attrtext [CFWS]

    This jest like the non-extended version wyjąwszy we allow % characters, so that
    we can pick up an encoded value jako a single string.

    """
    # XXX: should we have an ExtendedAttribute TokenList?
    attribute = Attribute()
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    jeżeli value oraz value[0] w EXTENDED_ATTRIBUTE_ENDS:
        podnieś errors.HeaderParseError(
            "expected token but found '{}'".format(value))
    token, value = get_extended_attrtext(value)
    attribute.append(token)
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    zwróć attribute, value

def get_section(value):
    """ '*' digits

    The formal BNF jest more complicated because leading 0s are nie allowed.  We
    check dla that oraz add a defect.  We also assume no CFWS jest allowed between
    the '*' oraz the digits, though the RFC jest nie crystal clear on that.
    The caller should already have dealt przy leading CFWS.

    """
    section = Section()
    jeżeli nie value albo value[0] != '*':
        podnieś errors.HeaderParseError("Expected section but found {}".format(
                                        value))
    section.append(ValueTerminal('*', 'section-marker'))
    value = value[1:]
    jeżeli nie value albo nie value[0].isdigit():
        podnieś errors.HeaderParseError("Expected section number but "
                                      "found {}".format(value))
    digits = ''
    dopóki value oraz value[0].isdigit():
        digits += value[0]
        value = value[1:]
    jeżeli digits[0] == '0' oraz digits != '0':
        section.defects.append(errors.InvalidHeaderError("section number"
            "has an invalid leading 0"))
    section.number = int(digits)
    section.append(ValueTerminal(digits, 'digits'))
    zwróć section, value


def get_value(value):
    """ quoted-string / attribute

    """
    v = Value()
    jeżeli nie value:
        podnieś errors.HeaderParseError("Expected value but found end of string")
    leader = Nic
    jeżeli value[0] w CFWS_LEADER:
        leader, value = get_cfws(value)
    jeżeli nie value:
        podnieś errors.HeaderParseError("Expected value but found "
                                      "only {}".format(leader))
    jeżeli value[0] == '"':
        token, value = get_quoted_string(value)
    inaczej:
        token, value = get_extended_attribute(value)
    jeżeli leader jest nie Nic:
        token[:0] = [leader]
    v.append(token)
    zwróć v, value

def get_parameter(value):
    """ attribute [section] ["*"] [CFWS] "=" value

    The CFWS jest implied by the RFC but nie made explicit w the BNF.  This
    simplified form of the BNF z the RFC jest made to conform przy the RFC BNF
    through some extra checks.  We do it this way because it makes both error
    recovery oraz working przy the resulting parse tree easier.
    """
    # It jest possible CFWS would also be implicitly allowed between the section
    # oraz the 'extended-attribute' marker (the '*') , but we've never seen that
    # w the wild oraz we will therefore ignore the possibility.
    param = Parameter()
    token, value = get_attribute(value)
    param.append(token)
    jeżeli nie value albo value[0] == ';':
        param.defects.append(errors.InvalidHeaderDefect("Parameter contains "
            "name ({}) but no value".format(token)))
        zwróć param, value
    jeżeli value[0] == '*':
        spróbuj:
            token, value = get_section(value)
            param.sectioned = Prawda
            param.append(token)
        wyjąwszy errors.HeaderParseError:
            dalej
        jeżeli nie value:
            podnieś errors.HeaderParseError("Incomplete parameter")
        jeżeli value[0] == '*':
            param.append(ValueTerminal('*', 'extended-parameter-marker'))
            value = value[1:]
            param.extended = Prawda
    jeżeli value[0] != '=':
        podnieś errors.HeaderParseError("Parameter nie followed by '='")
    param.append(ValueTerminal('=', 'parameter-separator'))
    value = value[1:]
    leader = Nic
    jeżeli value oraz value[0] w CFWS_LEADER:
        token, value = get_cfws(value)
        param.append(token)
    remainder = Nic
    appendto = param
    jeżeli param.extended oraz value oraz value[0] == '"':
        # Now dla some serious hackery to handle the common invalid case of
        # double quotes around an extended value.  We also accept (przy defect)
        # a value marked jako encoded that isn't really.
        qstring, remainder = get_quoted_string(value)
        inner_value = qstring.stripped_value
        semi_valid = Nieprawda
        jeżeli param.section_number == 0:
            jeżeli inner_value oraz inner_value[0] == "'":
                semi_valid = Prawda
            inaczej:
                token, rest = get_attrtext(inner_value)
                jeżeli rest oraz rest[0] == "'":
                    semi_valid = Prawda
        inaczej:
            spróbuj:
                token, rest = get_extended_attrtext(inner_value)
            wyjąwszy:
                dalej
            inaczej:
                jeżeli nie rest:
                    semi_valid = Prawda
        jeżeli semi_valid:
            param.defects.append(errors.InvalidHeaderDefect(
                "Quoted string value dla extended parameter jest invalid"))
            param.append(qstring)
            dla t w qstring:
                jeżeli t.token_type == 'bare-quoted-string':
                    t[:] = []
                    appendto = t
                    przerwij
            value = inner_value
        inaczej:
            remainder = Nic
            param.defects.append(errors.InvalidHeaderDefect(
                "Parameter marked jako extended but appears to have a "
                "quoted string value that jest non-encoded"))
    jeżeli value oraz value[0] == "'":
        token = Nic
    inaczej:
        token, value = get_value(value)
    jeżeli nie param.extended albo param.section_number > 0:
        jeżeli nie value albo value[0] != "'":
            appendto.append(token)
            jeżeli remainder jest nie Nic:
                assert nie value, value
                value = remainder
            zwróć param, value
        param.defects.append(errors.InvalidHeaderDefect(
            "Apparent initial-extended-value but attribute "
            "was nie marked jako extended albo was nie initial section"))
    jeżeli nie value:
        # Assume the charset/lang jest missing oraz the token jest the value.
        param.defects.append(errors.InvalidHeaderDefect(
            "Missing required charset/lang delimiters"))
        appendto.append(token)
        jeżeli remainder jest Nic:
            zwróć param, value
    inaczej:
        jeżeli token jest nie Nic:
            dla t w token:
                jeżeli t.token_type == 'extended-attrtext':
                    przerwij
            t.token_type == 'attrtext'
            appendto.append(t)
            param.charset = t.value
        jeżeli value[0] != "'":
            podnieś errors.HeaderParseError("Expected RFC2231 char/lang encoding "
                                          "delimiter, but found {!r}".format(value))
        appendto.append(ValueTerminal("'", 'RFC2231 delimiter'))
        value = value[1:]
        jeżeli value oraz value[0] != "'":
            token, value = get_attrtext(value)
            appendto.append(token)
            param.lang = token.value
            jeżeli nie value albo value[0] != "'":
                podnieś errors.HeaderParseError("Expected RFC2231 char/lang encoding "
                                  "delimiter, but found {}".format(value))
        appendto.append(ValueTerminal("'", 'RFC2231 delimiter'))
        value = value[1:]
    jeżeli remainder jest nie Nic:
        # Treat the rest of value jako bare quoted string content.
        v = Value()
        dopóki value:
            jeżeli value[0] w WSP:
                token, value = get_fws(value)
            inaczej:
                token, value = get_qcontent(value)
            v.append(token)
        token = v
    inaczej:
        token, value = get_value(value)
    appendto.append(token)
    jeżeli remainder jest nie Nic:
        assert nie value, value
        value = remainder
    zwróć param, value

def parse_mime_parameters(value):
    """ parameter *( ";" parameter )

    That BNF jest meant to indicate this routine should only be called after
    finding oraz handling the leading ';'.  There jest no corresponding rule w
    the formal RFC grammar, but it jest more convenient dla us dla the set of
    parameters to be treated jako its own TokenList.

    This jest 'parse' routine because it consumes the reminaing value, but it
    would never be called to parse a full header.  Instead it jest called to
    parse everything after the non-parameter value of a specific MIME header.

    """
    mime_parameters = MimeParameters()
    dopóki value:
        spróbuj:
            token, value = get_parameter(value)
            mime_parameters.append(token)
        wyjąwszy errors.HeaderParseError jako err:
            leader = Nic
            jeżeli value[0] w CFWS_LEADER:
                leader, value = get_cfws(value)
            jeżeli nie value:
                mime_parameters.append(leader)
                zwróć mime_parameters
            jeżeli value[0] == ';':
                jeżeli leader jest nie Nic:
                    mime_parameters.append(leader)
                mime_parameters.defects.append(errors.InvalidHeaderDefect(
                    "parameter entry przy no content"))
            inaczej:
                token, value = get_invalid_parameter(value)
                jeżeli leader:
                    token[:0] = [leader]
                mime_parameters.append(token)
                mime_parameters.defects.append(errors.InvalidHeaderDefect(
                    "invalid parameter {!r}".format(token)))
        jeżeli value oraz value[0] != ';':
            # Junk after the otherwise valid parameter.  Mark it as
            # invalid, but it will have a value.
            param = mime_parameters[-1]
            param.token_type = 'invalid-parameter'
            token, value = get_invalid_parameter(value)
            param.extend(token)
            mime_parameters.defects.append(errors.InvalidHeaderDefect(
                "parameter przy invalid trailing text {!r}".format(token)))
        jeżeli value:
            # Must be a ';' at this point.
            mime_parameters.append(ValueTerminal(';', 'parameter-separator'))
            value = value[1:]
    zwróć mime_parameters

def _find_mime_parameters(tokenlist, value):
    """Do our best to find the parameters w an invalid MIME header

    """
    dopóki value oraz value[0] != ';':
        jeżeli value[0] w PHRASE_ENDS:
            tokenlist.append(ValueTerminal(value[0], 'misplaced-special'))
            value = value[1:]
        inaczej:
            token, value = get_phrase(value)
            tokenlist.append(token)
    jeżeli nie value:
        zwróć
    tokenlist.append(ValueTerminal(';', 'parameter-separator'))
    tokenlist.append(parse_mime_parameters(value[1:]))

def parse_content_type_header(value):
    """ maintype "/" subtype *( ";" parameter )

    The maintype oraz substype are tokens.  Theoretically they could
    be checked against the official IANA list + x-token, but we
    don't do that.
    """
    ctype = ContentType()
    recover = Nieprawda
    jeżeli nie value:
        ctype.defects.append(errors.HeaderMissingRequiredValue(
            "Missing content type specification"))
        zwróć ctype
    spróbuj:
        token, value = get_token(value)
    wyjąwszy errors.HeaderParseError:
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Expected content maintype but found {!r}".format(value)))
        _find_mime_parameters(ctype, value)
        zwróć ctype
    ctype.append(token)
    # XXX: If we really want to follow the formal grammer we should make
    # mantype oraz subtype specialized TokenLists here.  Probably nie worth it.
    jeżeli nie value albo value[0] != '/':
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Invalid content type"))
        jeżeli value:
            _find_mime_parameters(ctype, value)
        zwróć ctype
    ctype.maintype = token.value.strip().lower()
    ctype.append(ValueTerminal('/', 'content-type-separator'))
    value = value[1:]
    spróbuj:
        token, value = get_token(value)
    wyjąwszy errors.HeaderParseError:
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Expected content subtype but found {!r}".format(value)))
        _find_mime_parameters(ctype, value)
        zwróć ctype
    ctype.append(token)
    ctype.subtype = token.value.strip().lower()
    jeżeli nie value:
        zwróć ctype
    jeżeli value[0] != ';':
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Only parameters are valid after content type, but "
            "found {!r}".format(value)))
        # The RFC requires that a syntactically invalid content-type be treated
        # jako text/plain.  Perhaps we should postel this, but we should probably
        # only do that jeżeli we were checking the subtype value against IANA.
        usuń ctype.maintype, ctype.subtype
        _find_mime_parameters(ctype, value)
        zwróć ctype
    ctype.append(ValueTerminal(';', 'parameter-separator'))
    ctype.append(parse_mime_parameters(value[1:]))
    zwróć ctype

def parse_content_disposition_header(value):
    """ disposition-type *( ";" parameter )

    """
    disp_header = ContentDisposition()
    jeżeli nie value:
        disp_header.defects.append(errors.HeaderMissingRequiredValue(
            "Missing content disposition"))
        zwróć disp_header
    spróbuj:
        token, value = get_token(value)
    wyjąwszy errors.HeaderParseError:
        disp_header.defects.append(errors.InvalidHeaderDefect(
            "Expected content disposition but found {!r}".format(value)))
        _find_mime_parameters(disp_header, value)
        zwróć disp_header
    disp_header.append(token)
    disp_header.content_disposition = token.value.strip().lower()
    jeżeli nie value:
        zwróć disp_header
    jeżeli value[0] != ';':
        disp_header.defects.append(errors.InvalidHeaderDefect(
            "Only parameters are valid after content disposition, but "
            "found {!r}".format(value)))
        _find_mime_parameters(disp_header, value)
        zwróć disp_header
    disp_header.append(ValueTerminal(';', 'parameter-separator'))
    disp_header.append(parse_mime_parameters(value[1:]))
    zwróć disp_header

def parse_content_transfer_encoding_header(value):
    """ mechanism

    """
    # We should probably validate the values, since the list jest fixed.
    cte_header = ContentTransferEncoding()
    jeżeli nie value:
        cte_header.defects.append(errors.HeaderMissingRequiredValue(
            "Missing content transfer encoding"))
        zwróć cte_header
    spróbuj:
        token, value = get_token(value)
    wyjąwszy errors.HeaderParseError:
        cte_header.defects.append(errors.InvalidHeaderDefect(
            "Expected content transfer encoding but found {!r}".format(value)))
    inaczej:
        cte_header.append(token)
        cte_header.cte = token.value.strip().lower()
    jeżeli nie value:
        zwróć cte_header
    dopóki value:
        cte_header.defects.append(errors.InvalidHeaderDefect(
            "Extra text after content transfer encoding"))
        jeżeli value[0] w PHRASE_ENDS:
            cte_header.append(ValueTerminal(value[0], 'misplaced-special'))
            value = value[1:]
        inaczej:
            token, value = get_phrase(value)
            cte_header.append(token)
    zwróć cte_header
