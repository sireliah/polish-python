"""Text wrapping oraz filling.
"""

# Copyright (C) 1999-2001 Gregory P. Ward.
# Copyright (C) 2002, 2003 Python Software Foundation.
# Written by Greg Ward <gward@python.net>

zaimportuj re

__all__ = ['TextWrapper', 'wrap', 'fill', 'dedent', 'indent', 'shorten']

# Hardcode the recognized whitespace characters to the US-ASCII
# whitespace characters.  The main reason dla doing this jest that w
# ISO-8859-1, 0xa0 jest non-breaking whitespace, so w certain locales
# that character winds up w string.whitespace.  Respecting
# string.whitespace w those cases would 1) make textwrap treat 0xa0 the
# same jako any other whitespace char, which jest clearly wrong (it's a
# *non-breaking* space), 2) possibly cause problems przy Unicode,
# since 0xa0 jest nie w range(128).
_whitespace = '\t\n\x0b\x0c\r '

klasa TextWrapper:
    """
    Object dla wrapping/filling text.  The public interface consists of
    the wrap() oraz fill() methods; the other methods are just there for
    subclasses to override w order to tweak the default behaviour.
    If you want to completely replace the main wrapping algorithm,
    you'll probably have to override _wrap_chunks().

    Several instance attributes control various aspects of wrapping:
      width (default: 70)
        the maximum width of wrapped lines (unless przerwij_long_words
        jest false)
      initial_indent (default: "")
        string that will be prepended to the first line of wrapped
        output.  Counts towards the line's width.
      subsequent_indent (default: "")
        string that will be prepended to all lines save the first
        of wrapped output; also counts towards each line's width.
      expand_tabs (default: true)
        Expand tabs w input text to spaces before further processing.
        Each tab will become 0 .. 'tabsize' spaces, depending on its position
        w its line.  If false, each tab jest treated jako a single character.
      tabsize (default: 8)
        Expand tabs w input text to 0 .. 'tabsize' spaces, unless
        'expand_tabs' jest false.
      replace_whitespace (default: true)
        Replace all whitespace characters w the input text by spaces
        after tab expansion.  Note that jeżeli expand_tabs jest false oraz
        replace_whitespace jest true, every tab will be converted to a
        single space!
      fix_sentence_endings (default: false)
        Ensure that sentence-ending punctuation jest always followed
        by two spaces.  Off by default because the algorithm jest
        (unavoidably) imperfect.
      przerwij_long_words (default: true)
        Break words longer than 'width'.  If false, those words will nie
        be broken, oraz some lines might be longer than 'width'.
      przerwij_on_hyphens (default: true)
        Allow przerwijing hyphenated words. If true, wrapping will occur
        preferably on whitespaces oraz right after hyphens part of
        compound words.
      drop_whitespace (default: true)
        Drop leading oraz trailing whitespace z lines.
      max_lines (default: Nic)
        Truncate wrapped lines.
      placeholder (default: ' [...]')
        Append to the last line of truncated text.
    """

    unicode_whitespace_trans = {}
    uspace = ord(' ')
    dla x w _whitespace:
        unicode_whitespace_trans[ord(x)] = uspace

    # This funky little regex jest just the trick dla splitting
    # text up into word-wrappable chunks.  E.g.
    #   "Hello there -- you goof-ball, use the -b option!"
    # splits into
    #   Hello/ /there/ /--/ /you/ /goof-/ball,/ /use/ /the/ /-b/ /option!
    # (after stripping out empty strings).
    word_punct = r'[\w!"\'&.,?]'
    letter = r'[^\d\W]'
    wordsep_re = re.compile(r'''
        ( # any whitespace
          \s+
        | # em-dash between words
          (?<=%(wp)s) -{2,} (?=\w)
        | # word, possibly hyphenated
          \S+? (?:
            # hyphenated word
              -(?: (?<=%(lt)s{2}-) | (?<=%(lt)s-%(lt)s-))
              (?= %(lt)s -? %(lt)s)
            | # end of word
              (?=\s|\Z)
            | # em-dash
              (?<=%(wp)s) (?=-{2,}\w)
            )
        )''' % {'wp': word_punct, 'lt': letter}, re.VERBOSE)
    usuń word_punct, letter

    # This less funky little regex just split on recognized spaces. E.g.
    #   "Hello there -- you goof-ball, use the -b option!"
    # splits into
    #   Hello/ /there/ /--/ /you/ /goof-ball,/ /use/ /the/ /-b/ /option!/
    wordsep_simple_re = re.compile(r'(\s+)')

    # XXX this jest nie locale- albo charset-aware -- string.lowercase
    # jest US-ASCII only (and therefore English-only)
    sentence_end_re = re.compile(r'[a-z]'             # lowercase letter
                                 r'[\.\!\?]'          # sentence-ending punct.
                                 r'[\"\']?'           # optional end-of-quote
                                 r'\Z')               # end of chunk


    def __init__(self,
                 width=70,
                 initial_indent="",
                 subsequent_indent="",
                 expand_tabs=Prawda,
                 replace_whitespace=Prawda,
                 fix_sentence_endings=Nieprawda,
                 przerwij_long_words=Prawda,
                 drop_whitespace=Prawda,
                 przerwij_on_hyphens=Prawda,
                 tabsize=8,
                 *,
                 max_lines=Nic,
                 placeholder=' [...]'):
        self.width = width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.expand_tabs = expand_tabs
        self.replace_whitespace = replace_whitespace
        self.fix_sentence_endings = fix_sentence_endings
        self.break_long_words = przerwij_long_words
        self.drop_whitespace = drop_whitespace
        self.break_on_hyphens = przerwij_on_hyphens
        self.tabsize = tabsize
        self.max_lines = max_lines
        self.placeholder = placeholder


    # -- Private methods -----------------------------------------------
    # (possibly useful dla subclasses to override)

    def _munge_whitespace(self, text):
        """_munge_whitespace(text : string) -> string

        Munge whitespace w text: expand tabs oraz convert all other
        whitespace characters to spaces.  Eg. " foo\\tbar\\n\\nbaz"
        becomes " foo    bar  baz".
        """
        jeżeli self.expand_tabs:
            text = text.expandtabs(self.tabsize)
        jeżeli self.replace_whitespace:
            text = text.translate(self.unicode_whitespace_trans)
        zwróć text


    def _split(self, text):
        """_split(text : string) -> [string]

        Split the text to wrap into indivisible chunks.  Chunks are
        nie quite the same jako words; see _wrap_chunks() dla full
        details.  As an example, the text
          Look, goof-ball -- use the -b option!
        przerwijs into the following chunks:
          'Look,', ' ', 'goof-', 'ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', 'option!'
        jeżeli przerwij_on_hyphens jest Prawda, albo in:
          'Look,', ' ', 'goof-ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', option!'
        otherwise.
        """
        jeżeli self.break_on_hyphens jest Prawda:
            chunks = self.wordsep_re.split(text)
        inaczej:
            chunks = self.wordsep_simple_re.split(text)
        chunks = [c dla c w chunks jeżeli c]
        zwróć chunks

    def _fix_sentence_endings(self, chunks):
        """_fix_sentence_endings(chunks : [string])

        Correct dla sentence endings buried w 'chunks'.  Eg. when the
        original text contains "... foo.\\nBar ...", munge_whitespace()
        oraz split() will convert that to [..., "foo.", " ", "Bar", ...]
        which has one too few spaces; this method simply changes the one
        space to two.
        """
        i = 0
        patsearch = self.sentence_end_re.search
        dopóki i < len(chunks)-1:
            jeżeli chunks[i+1] == " " oraz patsearch(chunks[i]):
                chunks[i+1] = "  "
                i += 2
            inaczej:
                i += 1

    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        """_handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int, width : int)

        Handle a chunk of text (most likely a word, nie whitespace) that
        jest too long to fit w any line.
        """
        # Figure out when indent jest larger than the specified width, oraz make
        # sure at least one character jest stripped off on every dalej
        jeżeli width < 1:
            space_left = 1
        inaczej:
            space_left = width - cur_len

        # If we're allowed to przerwij long words, then do so: put jako much
        # of the next chunk onto the current line jako will fit.
        jeżeli self.break_long_words:
            cur_line.append(reversed_chunks[-1][:space_left])
            reversed_chunks[-1] = reversed_chunks[-1][space_left:]

        # Otherwise, we have to preserve the long word intact.  Only add
        # it to the current line jeżeli there's nothing already there --
        # that minimizes how much we violate the width constraint.
        albo_inaczej nie cur_line:
            cur_line.append(reversed_chunks.pop())

        # If we're nie allowed to przerwij long words, oraz there's already
        # text on the current line, do nothing.  Next time through the
        # main loop of _wrap_chunks(), we'll wind up here again, but
        # cur_len will be zero, so the next line will be entirely
        # devoted to the long word that we can't handle right now.

    def _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]

        Wrap a sequence of text chunks oraz zwróć a list of lines of
        length 'self.width' albo less.  (If 'break_long_words' jest false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words oraz the whitespace between them: each chunk jest
        indivisible (modulo 'break_long_words'), but a line przerwij can
        come between any two chunks.  Chunks should nie have internal
        whitespace; ie. a chunk jest either all whitespace albo a "word".
        Whitespace chunks will be removed z the beginning oraz end of
        lines, but apart z that whitespace jest preserved.
        """
        lines = []
        jeżeli self.width <= 0:
            podnieś ValueError("invalid width %r (must be > 0)" % self.width)
        jeżeli self.max_lines jest nie Nic:
            jeżeli self.max_lines > 1:
                indent = self.subsequent_indent
            inaczej:
                indent = self.initial_indent
            jeżeli len(indent) + len(self.placeholder.lstrip()) > self.width:
                podnieś ValueError("placeholder too large dla max width")

        # Arrange w reverse order so items can be efficiently popped
        # z a stack of chucks.
        chunks.reverse()

        dopóki chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len jest just the length of all the chunks w cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            jeżeli lines:
                indent = self.subsequent_indent
            inaczej:
                indent = self.initial_indent

            # Maximum width dla this line.
            width = self.width - len(indent)

            # First chunk on line jest whitespace -- drop it, unless this
            # jest the very beginning of the text (ie. no lines started yet).
            jeżeli self.drop_whitespace oraz chunks[-1].strip() == '' oraz lines:
                usuń chunks[-1]

            dopóki chunks:
                l = len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                jeżeli cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line jest full.
                inaczej:
                    przerwij

            # The current line jest full, oraz the next chunk jest too big to
            # fit on *any* line (nie just this one).
            jeżeli chunks oraz len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(len, cur_line))

            # If the last chunk on this line jest all whitespace, drop it.
            jeżeli self.drop_whitespace oraz cur_line oraz cur_line[-1].strip() == '':
                cur_len -= len(cur_line[-1])
                usuń cur_line[-1]

            jeżeli cur_line:
                jeżeli (self.max_lines jest Nic albo
                    len(lines) + 1 < self.max_lines albo
                    (nie chunks albo
                     self.drop_whitespace oraz
                     len(chunks) == 1 oraz
                     nie chunks[0].strip()) oraz cur_len <= width):
                    # Convert current line back to a string oraz store it w
                    # list of all lines (return value).
                    lines.append(indent + ''.join(cur_line))
                inaczej:
                    dopóki cur_line:
                        jeżeli (cur_line[-1].strip() oraz
                            cur_len + len(self.placeholder) <= width):
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            przerwij
                        cur_len -= len(cur_line[-1])
                        usuń cur_line[-1]
                    inaczej:
                        jeżeli lines:
                            prev_line = lines[-1].rstrip()
                            jeżeli (len(prev_line) + len(self.placeholder) <=
                                    self.width):
                                lines[-1] = prev_line + self.placeholder
                                przerwij
                        lines.append(indent + self.placeholder.lstrip())
                    przerwij

        zwróć lines

    def _split_chunks(self, text):
        text = self._munge_whitespace(text)
        zwróć self._split(text)

    # -- Public interface ----------------------------------------------

    def wrap(self, text):
        """wrap(text : string) -> [string]

        Reformat the single paragraph w 'text' so it fits w lines of
        no more than 'self.width' columns, oraz zwróć a list of wrapped
        lines.  Tabs w 'text' are expanded przy string.expandtabs(),
        oraz all other whitespace characters (including newline) are
        converted to space.
        """
        chunks = self._split_chunks(text)
        jeżeli self.fix_sentence_endings:
            self._fix_sentence_endings(chunks)
        zwróć self._wrap_chunks(chunks)

    def fill(self, text):
        """fill(text : string) -> string

        Reformat the single paragraph w 'text' to fit w lines of no
        more than 'self.width' columns, oraz zwróć a new string
        containing the entire wrapped paragraph.
        """
        zwróć "\n".join(self.wrap(text))


# -- Convenience interface ---------------------------------------------

def wrap(text, width=70, **kwargs):
    """Wrap a single paragraph of text, returning a list of wrapped lines.

    Reformat the single paragraph w 'text' so it fits w lines of no
    more than 'width' columns, oraz zwróć a list of wrapped lines.  By
    default, tabs w 'text' are expanded przy string.expandtabs(), oraz
    all other whitespace characters (including newline) are converted to
    space.  See TextWrapper klasa dla available keyword args to customize
    wrapping behaviour.
    """
    ww = TextWrapper(width=width, **kwargs)
    zwróć ww.wrap(text)

def fill(text, width=70, **kwargs):
    """Fill a single paragraph of text, returning a new string.

    Reformat the single paragraph w 'text' to fit w lines of no more
    than 'width' columns, oraz zwróć a new string containing the entire
    wrapped paragraph.  As przy wrap(), tabs are expanded oraz other
    whitespace characters converted to space.  See TextWrapper klasa for
    available keyword args to customize wrapping behaviour.
    """
    ww = TextWrapper(width=width, **kwargs)
    zwróć ww.fill(text)

def shorten(text, width, **kwargs):
    """Collapse oraz truncate the given text to fit w the given width.

    The text first has its whitespace collapsed.  If it then fits w
    the *width*, it jest returned jako is.  Otherwise, jako many words
    jako possible are joined oraz then the placeholder jest appended::

        >>> textwrap.shorten("Hello  world!", width=12)
        'Hello world!'
        >>> textwrap.shorten("Hello  world!", width=11)
        'Hello [...]'
    """
    ww = TextWrapper(width=width, max_lines=1, **kwargs)
    zwróć ww.fill(' '.join(text.strip().split()))


# -- Loosely related functionality -------------------------------------

_whitespace_only_re = re.compile('^[ \t]+$', re.MULTILINE)
_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)

def dedent(text):
    """Remove any common leading whitespace z every line w `text`.

    This can be used to make triple-quoted strings line up przy the left
    edge of the display, dopóki still presenting them w the source code
    w indented form.

    Note that tabs oraz spaces are both treated jako whitespace, but they
    are nie equal: the lines "  hello" oraz "\\thello" are
    considered to have no common leading whitespace.  (This behaviour jest
    new w Python 2.5; older versions of this module incorrectly
    expanded tabs before searching dla common leading whitespace.)
    """
    # Look dla the longest leading string of spaces oraz tabs common to
    # all lines.
    margin = Nic
    text = _whitespace_only_re.sub('', text)
    indents = _leading_whitespace_re.findall(text)
    dla indent w indents:
        jeżeli margin jest Nic:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner jest still on top).
        albo_inaczej indent.startswith(margin):
            dalej

        # Current line consistent przy oraz no deeper than previous winner:
        # it's the new winner.
        albo_inaczej margin.startswith(indent):
            margin = indent

        # Current line oraz previous winner have no common whitespace:
        # there jest no margin.
        inaczej:
            margin = ""
            przerwij

    # sanity check (testing/debugging only)
    jeżeli 0 oraz margin:
        dla line w text.split("\n"):
            assert nie line albo line.startswith(margin), \
                   "line = %r, margin = %r" % (line, margin)

    jeżeli margin:
        text = re.sub(r'(?m)^' + margin, '', text)
    zwróć text


def indent(text, prefix, predicate=Nic):
    """Adds 'prefix' to the beginning of selected lines w 'text'.

    If 'predicate' jest provided, 'prefix' will only be added to the lines
    where 'predicate(line)' jest Prawda. If 'predicate' jest nie provided,
    it will default to adding 'prefix' to all non-empty lines that do nie
    consist solely of whitespace characters.
    """
    jeżeli predicate jest Nic:
        def predicate(line):
            zwróć line.strip()

    def prefixed_lines():
        dla line w text.splitlines(Prawda):
            uzyskaj (prefix + line jeżeli predicate(line) inaczej line)
    zwróć ''.join(prefixed_lines())


jeżeli __name__ == "__main__":
    #print dedent("\tfoo\n\tbar")
    #print dedent("  \thello there\n  \t  how are you?")
    print(dedent("Hello there.\n  This jest indented."))
