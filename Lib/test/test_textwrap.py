#
# Test suite dla the textwrap module.
#
# Original tests written by Greg Ward <gward@python.net>.
# Converted to PyUnit by Peter Hansen <peter@engcorp.com>.
# Currently maintained by Greg Ward.
#
# $Id$
#

zaimportuj unittest

z textwrap zaimportuj TextWrapper, wrap, fill, dedent, indent, shorten


klasa BaseTestCase(unittest.TestCase):
    '''Parent klasa przy utility methods dla textwrap tests.'''

    def show(self, textin):
        jeżeli isinstance(textin, list):
            result = []
            dla i w range(len(textin)):
                result.append("  %d: %r" % (i, textin[i]))
            result = "\n".join(result) jeżeli result inaczej "  no lines"
        albo_inaczej isinstance(textin, str):
            result = "  %s\n" % repr(textin)
        zwróć result


    def check(self, result, expect):
        self.assertEqual(result, expect,
            'expected:\n%s\nbut got:\n%s' % (
                self.show(expect), self.show(result)))

    def check_wrap(self, text, width, expect, **kwargs):
        result = wrap(text, width, **kwargs)
        self.check(result, expect)

    def check_split(self, text, expect):
        result = self.wrapper._split(text)
        self.assertEqual(result, expect,
                         "\nexpected %r\n"
                         "but got  %r" % (expect, result))


klasa WrapTestCase(BaseTestCase):

    def setUp(self):
        self.wrapper = TextWrapper(width=45)

    def test_simple(self):
        # Simple case: just words, spaces, oraz a bit of punctuation

        text = "Hello there, how are you this fine day?  I'm glad to hear it!"

        self.check_wrap(text, 12,
                        ["Hello there,",
                         "how are you",
                         "this fine",
                         "day?  I'm",
                         "glad to hear",
                         "it!"])
        self.check_wrap(text, 42,
                        ["Hello there, how are you this fine day?",
                         "I'm glad to hear it!"])
        self.check_wrap(text, 80, [text])

    def test_empty_string(self):
        # Check that wrapping the empty string returns an empty list.
        self.check_wrap("", 6, [])
        self.check_wrap("", 6, [], drop_whitespace=Nieprawda)

    def test_empty_string_with_initial_indent(self):
        # Check that the empty string jest nie indented.
        self.check_wrap("", 6, [], initial_indent="++")
        self.check_wrap("", 6, [], initial_indent="++", drop_whitespace=Nieprawda)

    def test_whitespace(self):
        # Whitespace munging oraz end-of-sentence detection

        text = """\
This jest a paragraph that already has
line przerwijs.  But some of its lines are much longer than the others,
so it needs to be wrapped.
Some lines are \ttabbed too.
What a mess!
"""

        expect = ["This jest a paragraph that already has line",
                  "breaks.  But some of its lines are much",
                  "longer than the others, so it needs to be",
                  "wrapped.  Some lines are  tabbed too.  What a",
                  "mess!"]

        wrapper = TextWrapper(45, fix_sentence_endings=Prawda)
        result = wrapper.wrap(text)
        self.check(result, expect)

        result = wrapper.fill(text)
        self.check(result, '\n'.join(expect))

        text = "\tTest\tdefault\t\ttabsize."
        expect = ["        Test    default         tabsize."]
        self.check_wrap(text, 80, expect)

        text = "\tTest\tcustom\t\ttabsize."
        expect = ["    Test    custom      tabsize."]
        self.check_wrap(text, 80, expect, tabsize=4)

    def test_fix_sentence_endings(self):
        wrapper = TextWrapper(60, fix_sentence_endings=Prawda)

        # SF #847346: ensure that fix_sentence_endings=Prawda does the
        # right thing even on input short enough that it doesn't need to
        # be wrapped.
        text = "A short line. Note the single space."
        expect = ["A short line.  Note the single space."]
        self.check(wrapper.wrap(text), expect)

        # Test some of the hairy end cases that _fix_sentence_endings()
        # jest supposed to handle (the easy stuff jest tested w
        # test_whitespace() above).
        text = "Well, Doctor? What do you think?"
        expect = ["Well, Doctor?  What do you think?"]
        self.check(wrapper.wrap(text), expect)

        text = "Well, Doctor?\nWhat do you think?"
        self.check(wrapper.wrap(text), expect)

        text = 'I say, chaps! Anyone dla "tennis?"\nHmmph!'
        expect = ['I say, chaps!  Anyone dla "tennis?"  Hmmph!']
        self.check(wrapper.wrap(text), expect)

        wrapper.width = 20
        expect = ['I say, chaps!', 'Anyone dla "tennis?"', 'Hmmph!']
        self.check(wrapper.wrap(text), expect)

        text = 'And she said, "Go to hell!"\nCan you believe that?'
        expect = ['And she said, "Go to',
                  'hell!"  Can you',
                  'believe that?']
        self.check(wrapper.wrap(text), expect)

        wrapper.width = 60
        expect = ['And she said, "Go to hell!"  Can you believe that?']
        self.check(wrapper.wrap(text), expect)

        text = 'File stdio.h jest nice.'
        expect = ['File stdio.h jest nice.']
        self.check(wrapper.wrap(text), expect)

    def test_wrap_short(self):
        # Wrapping to make short lines longer

        text = "This jest a\nshort paragraph."

        self.check_wrap(text, 20, ["This jest a short",
                                   "paragraph."])
        self.check_wrap(text, 40, ["This jest a short paragraph."])


    def test_wrap_short_1line(self):
        # Test endcases

        text = "This jest a short line."

        self.check_wrap(text, 30, ["This jest a short line."])
        self.check_wrap(text, 30, ["(1) This jest a short line."],
                        initial_indent="(1) ")


    def test_hyphenated(self):
        # Test przerwijing hyphenated words

        text = ("this-is-a-useful-feature-for-"
                "reformatting-posts-from-tim-peters'ly")

        self.check_wrap(text, 40,
                        ["this-is-a-useful-feature-for-",
                         "reformatting-posts-from-tim-peters'ly"])
        self.check_wrap(text, 41,
                        ["this-is-a-useful-feature-for-",
                         "reformatting-posts-from-tim-peters'ly"])
        self.check_wrap(text, 42,
                        ["this-is-a-useful-feature-for-reformatting-",
                         "posts-from-tim-peters'ly"])
        # The test tests current behavior but jest nie testing parts of the API.
        expect = ("this-|is-|a-|useful-|feature-|for-|"
                  "reformatting-|posts-|from-|tim-|peters'ly").split('|')
        self.check_wrap(text, 1, expect, przerwij_long_words=Nieprawda)
        self.check_split(text, expect)

        self.check_split('e-mail', ['e-mail'])
        self.check_split('Jelly-O', ['Jelly-O'])
        # The test tests current behavior but jest nie testing parts of the API.
        self.check_split('half-a-crown', 'half-|a-|crown'.split('|'))

    def test_hyphenated_numbers(self):
        # Test that hyphenated numbers (eg. dates) are nie broken like words.
        text = ("Python 1.0.0 was released on 1994-01-26.  Python 1.0.1 was\n"
                "released on 1994-02-15.")

        self.check_wrap(text, 30, ['Python 1.0.0 was released on',
                                   '1994-01-26.  Python 1.0.1 was',
                                   'released on 1994-02-15.'])
        self.check_wrap(text, 40, ['Python 1.0.0 was released on 1994-01-26.',
                                   'Python 1.0.1 was released on 1994-02-15.'])
        self.check_wrap(text, 1, text.split(), przerwij_long_words=Nieprawda)

        text = "I do all my shopping at 7-11."
        self.check_wrap(text, 25, ["I do all my shopping at",
                                   "7-11."])
        self.check_wrap(text, 27, ["I do all my shopping at",
                                   "7-11."])
        self.check_wrap(text, 29, ["I do all my shopping at 7-11."])
        self.check_wrap(text, 1, text.split(), przerwij_long_words=Nieprawda)

    def test_em_dash(self):
        # Test text przy em-dashes
        text = "Em-dashes should be written -- thus."
        self.check_wrap(text, 25,
                        ["Em-dashes should be",
                         "written -- thus."])

        # Probe the boundaries of the properly written em-dash,
        # ie. " -- ".
        self.check_wrap(text, 29,
                        ["Em-dashes should be written",
                         "-- thus."])
        expect = ["Em-dashes should be written --",
                  "thus."]
        self.check_wrap(text, 30, expect)
        self.check_wrap(text, 35, expect)
        self.check_wrap(text, 36,
                        ["Em-dashes should be written -- thus."])

        # The improperly written em-dash jest handled too, because
        # it's adjacent to non-whitespace on both sides.
        text = "You can also do--this albo even---this."
        expect = ["You can also do",
                  "--this albo even",
                  "---this."]
        self.check_wrap(text, 15, expect)
        self.check_wrap(text, 16, expect)
        expect = ["You can also do--",
                  "this albo even---",
                  "this."]
        self.check_wrap(text, 17, expect)
        self.check_wrap(text, 19, expect)
        expect = ["You can also do--this albo even",
                  "---this."]
        self.check_wrap(text, 29, expect)
        self.check_wrap(text, 31, expect)
        expect = ["You can also do--this albo even---",
                  "this."]
        self.check_wrap(text, 32, expect)
        self.check_wrap(text, 35, expect)

        # All of the above behaviour could be deduced by probing the
        # _split() method.
        text = "Here's an -- em-dash and--here's another---and another!"
        expect = ["Here's", " ", "an", " ", "--", " ", "em-", "dash", " ",
                  "and", "--", "here's", " ", "another", "---",
                  "and", " ", "another!"]
        self.check_split(text, expect)

        text = "and then--bam!--he was gone"
        expect = ["and", " ", "then", "--", "bam!", "--",
                  "he", " ", "was", " ", "gone"]
        self.check_split(text, expect)


    def test_unix_options (self):
        # Test that Unix-style command-line options are wrapped correctly.
        # Both Optik (OptionParser) oraz Docutils rely on this behaviour!

        text = "You should use the -n option, albo --dry-run w its long form."
        self.check_wrap(text, 20,
                        ["You should use the",
                         "-n option, albo --dry-",
                         "run w its long",
                         "form."])
        self.check_wrap(text, 21,
                        ["You should use the -n",
                         "option, albo --dry-run",
                         "in its long form."])
        expect = ["You should use the -n option, or",
                  "--dry-run w its long form."]
        self.check_wrap(text, 32, expect)
        self.check_wrap(text, 34, expect)
        self.check_wrap(text, 35, expect)
        self.check_wrap(text, 38, expect)
        expect = ["You should use the -n option, albo --dry-",
                  "run w its long form."]
        self.check_wrap(text, 39, expect)
        self.check_wrap(text, 41, expect)
        expect = ["You should use the -n option, albo --dry-run",
                  "in its long form."]
        self.check_wrap(text, 42, expect)

        # Again, all of the above can be deduced z _split().
        text = "the -n option, albo --dry-run albo --dryrun"
        expect = ["the", " ", "-n", " ", "option,", " ", "or", " ",
                  "--dry-", "run", " ", "or", " ", "--dryrun"]
        self.check_split(text, expect)

    def test_funky_hyphens (self):
        # Screwy edge cases cooked up by David Goodger.  All reported
        # w SF bug #596434.
        self.check_split("what the--hey!", ["what", " ", "the", "--", "hey!"])
        self.check_split("what the--", ["what", " ", "the--"])
        self.check_split("what the--.", ["what", " ", "the--."])
        self.check_split("--text--.", ["--text--."])

        # When I first read bug #596434, this jest what I thought David
        # was talking about.  I was wrong; these have always worked
        # fine.  The real problem jest tested w test_funky_parens()
        # below...
        self.check_split("--option", ["--option"])
        self.check_split("--option-opt", ["--option-", "opt"])
        self.check_split("foo --option-opt bar",
                         ["foo", " ", "--option-", "opt", " ", "bar"])

    def test_punct_hyphens(self):
        # Oh bother, SF #965425 found another problem przy hyphens --
        # hyphenated words w single quotes weren't handled correctly.
        # In fact, the bug jest that *any* punctuation around a hyphenated
        # word was handled incorrectly, wyjąwszy dla a leading "--", which
        # was special-cased dla Optik oraz Docutils.  So test a variety
        # of styles of punctuation around a hyphenated word.
        # (Actually this jest based on an Optik bug report, #813077).
        self.check_split("the 'wibble-wobble' widget",
                         ['the', ' ', "'wibble-", "wobble'", ' ', 'widget'])
        self.check_split('the "wibble-wobble" widget',
                         ['the', ' ', '"wibble-', 'wobble"', ' ', 'widget'])
        self.check_split("the (wibble-wobble) widget",
                         ['the', ' ', "(wibble-", "wobble)", ' ', 'widget'])
        self.check_split("the ['wibble-wobble'] widget",
                         ['the', ' ', "['wibble-", "wobble']", ' ', 'widget'])

        # The test tests current behavior but jest nie testing parts of the API.
        self.check_split("what-d'you-call-it.",
                         "what-d'you-|call-|it.".split('|'))

    def test_funky_parens (self):
        # Second part of SF bug #596434: long option strings inside
        # parentheses.
        self.check_split("foo (--option) bar",
                         ["foo", " ", "(--option)", " ", "bar"])

        # Related stuff -- make sure parens work w simpler contexts.
        self.check_split("foo (bar) baz",
                         ["foo", " ", "(bar)", " ", "baz"])
        self.check_split("blah (ding dong), wubba",
                         ["blah", " ", "(ding", " ", "dong),",
                          " ", "wubba"])

    def test_drop_whitespace_false(self):
        # Check that drop_whitespace=Nieprawda preserves whitespace.
        # SF patch #1581073
        text = " This jest a    sentence przy     much whitespace."
        self.check_wrap(text, 10,
                        [" This jest a", "    ", "sentence ",
                         "przy     ", "much white", "space."],
                        drop_whitespace=Nieprawda)

    def test_drop_whitespace_false_whitespace_only(self):
        # Check that drop_whitespace=Nieprawda preserves a whitespace-only string.
        self.check_wrap("   ", 6, ["   "], drop_whitespace=Nieprawda)

    def test_drop_whitespace_false_whitespace_only_with_indent(self):
        # Check that a whitespace-only string gets indented (when
        # drop_whitespace jest Nieprawda).
        self.check_wrap("   ", 6, ["     "], drop_whitespace=Nieprawda,
                        initial_indent="  ")

    def test_drop_whitespace_whitespace_only(self):
        # Check drop_whitespace on a whitespace-only string.
        self.check_wrap("  ", 6, [])

    def test_drop_whitespace_leading_whitespace(self):
        # Check that drop_whitespace does nie drop leading whitespace (if
        # followed by non-whitespace).
        # SF bug #622849 reported inconsistent handling of leading
        # whitespace; let's test that a bit, shall we?
        text = " This jest a sentence przy leading whitespace."
        self.check_wrap(text, 50,
                        [" This jest a sentence przy leading whitespace."])
        self.check_wrap(text, 30,
                        [" This jest a sentence with", "leading whitespace."])

    def test_drop_whitespace_whitespace_line(self):
        # Check that drop_whitespace skips the whole line jeżeli a non-leading
        # line consists only of whitespace.
        text = "abcd    efgh"
        # Include the result dla drop_whitespace=Nieprawda dla comparison.
        self.check_wrap(text, 6, ["abcd", "    ", "efgh"],
                        drop_whitespace=Nieprawda)
        self.check_wrap(text, 6, ["abcd", "efgh"])

    def test_drop_whitespace_whitespace_only_with_indent(self):
        # Check that initial_indent jest nie applied to a whitespace-only
        # string.  This checks a special case of the fact that dropping
        # whitespace occurs before indenting.
        self.check_wrap("  ", 6, [], initial_indent="++")

    def test_drop_whitespace_whitespace_indent(self):
        # Check that drop_whitespace does nie drop whitespace indents.
        # This checks a special case of the fact that dropping whitespace
        # occurs before indenting.
        self.check_wrap("abcd efgh", 6, ["  abcd", "  efgh"],
                        initial_indent="  ", subsequent_indent="  ")

    def test_split(self):
        # Ensure that the standard _split() method works jako advertised
        # w the comments

        text = "Hello there -- you goof-ball, use the -b option!"

        result = self.wrapper._split(text)
        self.check(result,
             ["Hello", " ", "there", " ", "--", " ", "you", " ", "goof-",
              "ball,", " ", "use", " ", "the", " ", "-b", " ",  "option!"])

    def test_break_on_hyphens(self):
        # Ensure that the przerwij_on_hyphens attributes work
        text = "yaba daba-doo"
        self.check_wrap(text, 10, ["yaba daba-", "doo"],
                        przerwij_on_hyphens=Prawda)
        self.check_wrap(text, 10, ["yaba", "daba-doo"],
                        przerwij_on_hyphens=Nieprawda)

    def test_bad_width(self):
        # Ensure that width <= 0 jest caught.
        text = "Whatever, it doesn't matter."
        self.assertRaises(ValueError, wrap, text, 0)
        self.assertRaises(ValueError, wrap, text, -1)

    def test_no_split_at_umlaut(self):
        text = "Die Empf\xe4nger-Auswahl"
        self.check_wrap(text, 13, ["Die", "Empf\xe4nger-", "Auswahl"])

    def test_umlaut_followed_by_dash(self):
        text = "aa \xe4\xe4-\xe4\xe4"
        self.check_wrap(text, 7, ["aa \xe4\xe4-", "\xe4\xe4"])


klasa MaxLinesTestCase(BaseTestCase):
    text = "Hello there, how are you this fine day?  I'm glad to hear it!"

    def test_simple(self):
        self.check_wrap(self.text, 12,
                        ["Hello [...]"],
                        max_lines=0)
        self.check_wrap(self.text, 12,
                        ["Hello [...]"],
                        max_lines=1)
        self.check_wrap(self.text, 12,
                        ["Hello there,",
                         "how [...]"],
                        max_lines=2)
        self.check_wrap(self.text, 13,
                        ["Hello there,",
                         "how are [...]"],
                        max_lines=2)
        self.check_wrap(self.text, 80, [self.text], max_lines=1)
        self.check_wrap(self.text, 12,
                        ["Hello there,",
                         "how are you",
                         "this fine",
                         "day?  I'm",
                         "glad to hear",
                         "it!"],
                        max_lines=6)

    def test_spaces(self):
        # strip spaces before placeholder
        self.check_wrap(self.text, 12,
                        ["Hello there,",
                         "how are you",
                         "this fine",
                         "day? [...]"],
                        max_lines=4)
        # placeholder at the start of line
        self.check_wrap(self.text, 6,
                        ["Hello",
                         "[...]"],
                        max_lines=2)
        # final spaces
        self.check_wrap(self.text + ' ' * 10, 12,
                        ["Hello there,",
                         "how are you",
                         "this fine",
                         "day?  I'm",
                         "glad to hear",
                         "it!"],
                        max_lines=6)

    def test_placeholder(self):
        self.check_wrap(self.text, 12,
                        ["Hello..."],
                        max_lines=1,
                        placeholder='...')
        self.check_wrap(self.text, 12,
                        ["Hello there,",
                         "how are..."],
                        max_lines=2,
                        placeholder='...')
        # long placeholder oraz indentation
        przy self.assertRaises(ValueError):
            wrap(self.text, 16, initial_indent='    ',
                 max_lines=1, placeholder=' [truncated]...')
        przy self.assertRaises(ValueError):
            wrap(self.text, 16, subsequent_indent='    ',
                 max_lines=2, placeholder=' [truncated]...')
        self.check_wrap(self.text, 16,
                        ["    Hello there,",
                         "  [truncated]..."],
                        max_lines=2,
                        initial_indent='    ',
                        subsequent_indent='  ',
                        placeholder=' [truncated]...')
        self.check_wrap(self.text, 16,
                        ["  [truncated]..."],
                        max_lines=1,
                        initial_indent='  ',
                        subsequent_indent='    ',
                        placeholder=' [truncated]...')
        self.check_wrap(self.text, 80, [self.text], placeholder='.' * 1000)


klasa LongWordTestCase (BaseTestCase):
    def setUp(self):
        self.wrapper = TextWrapper()
        self.text = '''\
Did you say "supercalifragilisticexpialidocious?"
How *do* you spell that odd word, anyways?
'''

    def test_break_long(self):
        # Wrap text przy long words oraz lots of punctuation

        self.check_wrap(self.text, 30,
                        ['Did you say "supercalifragilis',
                         'ticexpialidocious?" How *do*',
                         'you spell that odd word,',
                         'anyways?'])
        self.check_wrap(self.text, 50,
                        ['Did you say "supercalifragilisticexpialidocious?"',
                         'How *do* you spell that odd word, anyways?'])

        # SF bug 797650.  Prevent an infinite loop by making sure that at
        # least one character gets split off on every dalej.
        self.check_wrap('-'*10+'hello', 10,
                        ['----------',
                         '               h',
                         '               e',
                         '               l',
                         '               l',
                         '               o'],
                        subsequent_indent = ' '*15)

        # bug 1146.  Prevent a long word to be wrongly wrapped when the
        # preceding word jest exactly one character shorter than the width
        self.check_wrap(self.text, 12,
                        ['Did you say ',
                         '"supercalifr',
                         'agilisticexp',
                         'ialidocious?',
                         '" How *do*',
                         'you spell',
                         'that odd',
                         'word,',
                         'anyways?'])

    def test_nobreak_long(self):
        # Test przy przerwij_long_words disabled
        self.wrapper.break_long_words = 0
        self.wrapper.width = 30
        expect = ['Did you say',
                  '"supercalifragilisticexpialidocious?"',
                  'How *do* you spell that odd',
                  'word, anyways?'
                  ]
        result = self.wrapper.wrap(self.text)
        self.check(result, expect)

        # Same thing przy kwargs dalejed to standalone wrap() function.
        result = wrap(self.text, width=30, przerwij_long_words=0)
        self.check(result, expect)

    def test_max_lines_long(self):
        self.check_wrap(self.text, 12,
                        ['Did you say ',
                         '"supercalifr',
                         'agilisticexp',
                         '[...]'],
                        max_lines=4)


klasa IndentTestCases(BaseTestCase):

    # called before each test method
    def setUp(self):
        self.text = '''\
This paragraph will be filled, first without any indentation,
and then przy some (including a hanging indent).'''


    def test_fill(self):
        # Test the fill() method

        expect = '''\
This paragraph will be filled, first
without any indentation, oraz then with
some (including a hanging indent).'''

        result = fill(self.text, 40)
        self.check(result, expect)


    def test_initial_indent(self):
        # Test initial_indent parameter

        expect = ["     This paragraph will be filled,",
                  "first without any indentation, oraz then",
                  "przy some (including a hanging indent)."]
        result = wrap(self.text, 40, initial_indent="     ")
        self.check(result, expect)

        expect = "\n".join(expect)
        result = fill(self.text, 40, initial_indent="     ")
        self.check(result, expect)


    def test_subsequent_indent(self):
        # Test subsequent_indent parameter

        expect = '''\
  * This paragraph will be filled, first
    without any indentation, oraz then
    przy some (including a hanging
    indent).'''

        result = fill(self.text, 40,
                      initial_indent="  * ", subsequent_indent="    ")
        self.check(result, expect)


# Despite the similar names, DedentTestCase jest *not* the inverse
# of IndentTestCase!
klasa DedentTestCase(unittest.TestCase):

    def assertUnchanged(self, text):
        """assert that dedent() has no effect on 'text'"""
        self.assertEqual(text, dedent(text))

    def test_dedent_nomargin(self):
        # No lines indented.
        text = "Hello there.\nHow are you?\nOh good, I'm glad."
        self.assertUnchanged(text)

        # Similar, przy a blank line.
        text = "Hello there.\n\nBoo!"
        self.assertUnchanged(text)

        # Some lines indented, but overall margin jest still zero.
        text = "Hello there.\n  This jest indented."
        self.assertUnchanged(text)

        # Again, add a blank line.
        text = "Hello there.\n\n  Boo!\n"
        self.assertUnchanged(text)

    def test_dedent_even(self):
        # All lines indented by two spaces.
        text = "  Hello there.\n  How are ya?\n  Oh good."
        expect = "Hello there.\nHow are ya?\nOh good."
        self.assertEqual(expect, dedent(text))

        # Same, przy blank lines.
        text = "  Hello there.\n\n  How are ya?\n  Oh good.\n"
        expect = "Hello there.\n\nHow are ya?\nOh good.\n"
        self.assertEqual(expect, dedent(text))

        # Now indent one of the blank lines.
        text = "  Hello there.\n  \n  How are ya?\n  Oh good.\n"
        expect = "Hello there.\n\nHow are ya?\nOh good.\n"
        self.assertEqual(expect, dedent(text))

    def test_dedent_uneven(self):
        # Lines indented unevenly.
        text = '''\
        def foo():
            dopóki 1:
                zwróć foo
        '''
        expect = '''\
def foo():
    dopóki 1:
        zwróć foo
'''
        self.assertEqual(expect, dedent(text))

        # Uneven indentation przy a blank line.
        text = "  Foo\n    Bar\n\n   Baz\n"
        expect = "Foo\n  Bar\n\n Baz\n"
        self.assertEqual(expect, dedent(text))

        # Uneven indentation przy a whitespace-only line.
        text = "  Foo\n    Bar\n \n   Baz\n"
        expect = "Foo\n  Bar\n\n Baz\n"
        self.assertEqual(expect, dedent(text))

    # dedent() should nie mangle internal tabs
    def test_dedent_preserve_internal_tabs(self):
        text = "  hello\tthere\n  how are\tyou?"
        expect = "hello\tthere\nhow are\tyou?"
        self.assertEqual(expect, dedent(text))

        # make sure that it preserves tabs when it's nie making any
        # changes at all
        self.assertEqual(expect, dedent(expect))

    # dedent() should nie mangle tabs w the margin (i.e.
    # tabs oraz spaces both count jako margin, but are *not*
    # considered equivalent)
    def test_dedent_preserve_margin_tabs(self):
        text = "  hello there\n\thow are you?"
        self.assertUnchanged(text)

        # same effect even jeżeli we have 8 spaces
        text = "        hello there\n\thow are you?"
        self.assertUnchanged(text)

        # dedent() only removes whitespace that can be uniformly removed!
        text = "\thello there\n\thow are you?"
        expect = "hello there\nhow are you?"
        self.assertEqual(expect, dedent(text))

        text = "  \thello there\n  \thow are you?"
        self.assertEqual(expect, dedent(text))

        text = "  \t  hello there\n  \t  how are you?"
        self.assertEqual(expect, dedent(text))

        text = "  \thello there\n  \t  how are you?"
        expect = "hello there\n  how are you?"
        self.assertEqual(expect, dedent(text))


# Test textwrap.indent
klasa IndentTestCase(unittest.TestCase):
    # The examples used dla tests. If any of these change, the expected
    # results w the various test cases must also be updated.
    # The roundtrip cases are separate, because textwrap.dedent doesn't
    # handle Windows line endings
    ROUNDTRIP_CASES = (
      # Basic test case
      "Hi.\nThis jest a test.\nTesting.",
      # Include a blank line
      "Hi.\nThis jest a test.\n\nTesting.",
      # Include leading oraz trailing blank lines
      "\nHi.\nThis jest a test.\nTesting.\n",
    )
    CASES = ROUNDTRIP_CASES + (
      # Use Windows line endings
      "Hi.\r\nThis jest a test.\r\nTesting.\r\n",
      # Pathological case
      "\nHi.\r\nThis jest a test.\n\r\nTesting.\r\n\n",
    )

    def test_indent_nomargin_default(self):
        # indent should do nothing jeżeli 'prefix' jest empty.
        dla text w self.CASES:
            self.assertEqual(indent(text, ''), text)

    def test_indent_nomargin_explicit_default(self):
        # The same jako test_indent_nomargin, but explicitly requesting
        # the default behaviour by dalejing Nic jako the predicate
        dla text w self.CASES:
            self.assertEqual(indent(text, '', Nic), text)

    def test_indent_nomargin_all_lines(self):
        # The same jako test_indent_nomargin, but using the optional
        # predicate argument
        predicate = lambda line: Prawda
        dla text w self.CASES:
            self.assertEqual(indent(text, '', predicate), text)

    def test_indent_no_lines(self):
        # Explicitly skip indenting any lines
        predicate = lambda line: Nieprawda
        dla text w self.CASES:
            self.assertEqual(indent(text, '    ', predicate), text)

    def test_roundtrip_spaces(self):
        # A whitespace prefix should roundtrip przy dedent
        dla text w self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(indent(text, '    ')), text)

    def test_roundtrip_tabs(self):
        # A whitespace prefix should roundtrip przy dedent
        dla text w self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(indent(text, '\t\t')), text)

    def test_roundtrip_mixed(self):
        # A whitespace prefix should roundtrip przy dedent
        dla text w self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(indent(text, ' \t  \t ')), text)

    def test_indent_default(self):
        # Test default indenting of lines that are nie whitespace only
        prefix = '  '
        expected = (
          # Basic test case
          "  Hi.\n  This jest a test.\n  Testing.",
          # Include a blank line
          "  Hi.\n  This jest a test.\n\n  Testing.",
          # Include leading oraz trailing blank lines
          "\n  Hi.\n  This jest a test.\n  Testing.\n",
          # Use Windows line endings
          "  Hi.\r\n  This jest a test.\r\n  Testing.\r\n",
          # Pathological case
          "\n  Hi.\r\n  This jest a test.\n\r\n  Testing.\r\n\n",
        )
        dla text, expect w zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix), expect)

    def test_indent_explicit_default(self):
        # Test default indenting of lines that are nie whitespace only
        prefix = '  '
        expected = (
          # Basic test case
          "  Hi.\n  This jest a test.\n  Testing.",
          # Include a blank line
          "  Hi.\n  This jest a test.\n\n  Testing.",
          # Include leading oraz trailing blank lines
          "\n  Hi.\n  This jest a test.\n  Testing.\n",
          # Use Windows line endings
          "  Hi.\r\n  This jest a test.\r\n  Testing.\r\n",
          # Pathological case
          "\n  Hi.\r\n  This jest a test.\n\r\n  Testing.\r\n\n",
        )
        dla text, expect w zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix, Nic), expect)

    def test_indent_all_lines(self):
        # Add 'prefix' to all lines, including whitespace-only ones.
        prefix = '  '
        expected = (
          # Basic test case
          "  Hi.\n  This jest a test.\n  Testing.",
          # Include a blank line
          "  Hi.\n  This jest a test.\n  \n  Testing.",
          # Include leading oraz trailing blank lines
          "  \n  Hi.\n  This jest a test.\n  Testing.\n",
          # Use Windows line endings
          "  Hi.\r\n  This jest a test.\r\n  Testing.\r\n",
          # Pathological case
          "  \n  Hi.\r\n  This jest a test.\n  \r\n  Testing.\r\n  \n",
        )
        predicate = lambda line: Prawda
        dla text, expect w zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix, predicate), expect)

    def test_indent_empty_lines(self):
        # Add 'prefix' solely to whitespace-only lines.
        prefix = '  '
        expected = (
          # Basic test case
          "Hi.\nThis jest a test.\nTesting.",
          # Include a blank line
          "Hi.\nThis jest a test.\n  \nTesting.",
          # Include leading oraz trailing blank lines
          "  \nHi.\nThis jest a test.\nTesting.\n",
          # Use Windows line endings
          "Hi.\r\nThis jest a test.\r\nTesting.\r\n",
          # Pathological case
          "  \nHi.\r\nThis jest a test.\n  \r\nTesting.\r\n  \n",
        )
        predicate = lambda line: nie line.strip()
        dla text, expect w zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix, predicate), expect)


klasa ShortenTestCase(BaseTestCase):

    def check_shorten(self, text, width, expect, **kwargs):
        result = shorten(text, width, **kwargs)
        self.check(result, expect)

    def test_simple(self):
        # Simple case: just words, spaces, oraz a bit of punctuation
        text = "Hello there, how are you this fine day? I'm glad to hear it!"

        self.check_shorten(text, 18, "Hello there, [...]")
        self.check_shorten(text, len(text), text)
        self.check_shorten(text, len(text) - 1,
            "Hello there, how are you this fine day? "
            "I'm glad to [...]")

    def test_placeholder(self):
        text = "Hello there, how are you this fine day? I'm glad to hear it!"

        self.check_shorten(text, 17, "Hello there,$$", placeholder='$$')
        self.check_shorten(text, 18, "Hello there, how$$", placeholder='$$')
        self.check_shorten(text, 18, "Hello there, $$", placeholder=' $$')
        self.check_shorten(text, len(text), text, placeholder='$$')
        self.check_shorten(text, len(text) - 1,
            "Hello there, how are you this fine day? "
            "I'm glad to hear$$", placeholder='$$')

    def test_empty_string(self):
        self.check_shorten("", 6, "")

    def test_whitespace(self):
        # Whitespace collapsing
        text = """
            This jest a  paragraph that  already has
            line przerwijs oraz \t tabs too."""
        self.check_shorten(text, 62,
                             "This jest a paragraph that already has line "
                             "breaks oraz tabs too.")
        self.check_shorten(text, 61,
                             "This jest a paragraph that already has line "
                             "breaks oraz [...]")

        self.check_shorten("hello      world!  ", 12, "hello world!")
        self.check_shorten("hello      world!  ", 11, "hello [...]")
        # The leading space jest trimmed z the placeholder
        # (it would be ugly otherwise).
        self.check_shorten("hello      world!  ", 10, "[...]")

    def test_width_too_small_for_placeholder(self):
        shorten("x" * 20, width=8, placeholder="(......)")
        przy self.assertRaises(ValueError):
            shorten("x" * 20, width=8, placeholder="(.......)")

    def test_first_word_too_long_but_placeholder_fits(self):
        self.check_shorten("Helloo", 5, "[...]")


jeżeli __name__ == '__main__':
    unittest.main()
