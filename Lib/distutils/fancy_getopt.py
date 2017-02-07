"""distutils.fancy_getopt

Wrapper around the standard getopt module that provides the following
additional features:
  * short oraz long options are tied together
  * options have help strings, so fancy_getopt could potentially
    create a complete usage summary
  * options set attributes of a dalejed-in object
"""

zaimportuj sys, string, re
zaimportuj getopt
z distutils.errors zaimportuj *

# Much like command_re w distutils.core, this jest close to but nie quite
# the same jako a Python NAME -- except, w the spirit of most GNU
# utilities, we use '-' w place of '_'.  (The spirit of LISP lives on!)
# The similarities to NAME are again nie a coincidence...
longopt_pat = r'[a-zA-Z](?:[a-zA-Z0-9-]*)'
longopt_re = re.compile(r'^%s$' % longopt_pat)

# For recognizing "negative alias" options, eg. "quiet=!verbose"
neg_alias_re = re.compile("^(%s)=!(%s)$" % (longopt_pat, longopt_pat))

# This jest used to translate long options to legitimate Python identifiers
# (dla use jako attributes of some object).
longopt_xlate = str.maketrans('-', '_')

klasa FancyGetopt:
    """Wrapper around the standard 'getopt()' module that provides some
    handy extra functionality:
      * short oraz long options are tied together
      * options have help strings, oraz help text can be assembled
        z them
      * options set attributes of a dalejed-in object
      * boolean options can have "negative aliases" -- eg. if
        --quiet jest the "negative alias" of --verbose, then "--quiet"
        on the command line sets 'verbose' to false
    """

    def __init__(self, option_table=Nic):
        # The option table jest (currently) a list of tuples.  The
        # tuples may have 3 albo four values:
        #   (long_option, short_option, help_string [, repeatable])
        # jeżeli an option takes an argument, its long_option should have '='
        # appended; short_option should just be a single character, no ':'
        # w any case.  If a long_option doesn't have a corresponding
        # short_option, short_option should be Nic.  All option tuples
        # must have long options.
        self.option_table = option_table

        # 'option_index' maps long option names to entries w the option
        # table (ie. those 3-tuples).
        self.option_index = {}
        jeżeli self.option_table:
            self._build_index()

        # 'alias' records (duh) alias options; {'foo': 'bar'} means
        # --foo jest an alias dla --bar
        self.alias = {}

        # 'negative_alias' keeps track of options that are the boolean
        # opposite of some other option
        self.negative_alias = {}

        # These keep track of the information w the option table.  We
        # don't actually populate these structures until we're ready to
        # parse the command-line, since the 'option_table' dalejed w here
        # isn't necessarily the final word.
        self.short_opts = []
        self.long_opts = []
        self.short2long = {}
        self.attr_name = {}
        self.takes_arg = {}

        # And 'option_order' jest filled up w 'getopt()'; it records the
        # original order of options (and their values) on the command-line,
        # but expands short options, converts aliases, etc.
        self.option_order = []

    def _build_index(self):
        self.option_index.clear()
        dla option w self.option_table:
            self.option_index[option[0]] = option

    def set_option_table(self, option_table):
        self.option_table = option_table
        self._build_index()

    def add_option(self, long_option, short_option=Nic, help_string=Nic):
        jeżeli long_option w self.option_index:
            podnieś DistutilsGetoptError(
                  "option conflict: already an option '%s'" % long_option)
        inaczej:
            option = (long_option, short_option, help_string)
            self.option_table.append(option)
            self.option_index[long_option] = option

    def has_option(self, long_option):
        """Return true jeżeli the option table dla this parser has an
        option przy long name 'long_option'."""
        zwróć long_option w self.option_index

    def get_attr_name(self, long_option):
        """Translate long option name 'long_option' to the form it
        has jako an attribute of some object: ie., translate hyphens
        to underscores."""
        zwróć long_option.translate(longopt_xlate)

    def _check_alias_dict(self, aliases, what):
        assert isinstance(aliases, dict)
        dla (alias, opt) w aliases.items():
            jeżeli alias nie w self.option_index:
                podnieś DistutilsGetoptError(("invalid %s '%s': "
                       "option '%s' nie defined") % (what, alias, alias))
            jeżeli opt nie w self.option_index:
                podnieś DistutilsGetoptError(("invalid %s '%s': "
                       "aliased option '%s' nie defined") % (what, alias, opt))

    def set_aliases(self, alias):
        """Set the aliases dla this option parser."""
        self._check_alias_dict(alias, "alias")
        self.alias = alias

    def set_negative_aliases(self, negative_alias):
        """Set the negative aliases dla this option parser.
        'negative_alias' should be a dictionary mapping option names to
        option names, both the key oraz value must already be defined
        w the option table."""
        self._check_alias_dict(negative_alias, "negative alias")
        self.negative_alias = negative_alias

    def _grok_option_table(self):
        """Populate the various data structures that keep tabs on the
        option table.  Called by 'getopt()' before it can do anything
        worthwhile.
        """
        self.long_opts = []
        self.short_opts = []
        self.short2long.clear()
        self.repeat = {}

        dla option w self.option_table:
            jeżeli len(option) == 3:
                long, short, help = option
                repeat = 0
            albo_inaczej len(option) == 4:
                long, short, help, repeat = option
            inaczej:
                # the option table jest part of the code, so simply
                # assert that it jest correct
                podnieś ValueError("invalid option tuple: %r" % (option,))

            # Type- oraz value-check the option names
            jeżeli nie isinstance(long, str) albo len(long) < 2:
                podnieś DistutilsGetoptError(("invalid long option '%s': "
                       "must be a string of length >= 2") % long)

            jeżeli (nie ((short jest Nic) albo
                     (isinstance(short, str) oraz len(short) == 1))):
                podnieś DistutilsGetoptError("invalid short option '%s': "
                       "must a single character albo Nic" % short)

            self.repeat[long] = repeat
            self.long_opts.append(long)

            jeżeli long[-1] == '=':             # option takes an argument?
                jeżeli short: short = short + ':'
                long = long[0:-1]
                self.takes_arg[long] = 1
            inaczej:
                # Is option jest a "negative alias" dla some other option (eg.
                # "quiet" == "!verbose")?
                alias_to = self.negative_alias.get(long)
                jeżeli alias_to jest nie Nic:
                    jeżeli self.takes_arg[alias_to]:
                        podnieś DistutilsGetoptError(
                              "invalid negative alias '%s': "
                              "aliased option '%s' takes a value"
                              % (long, alias_to))

                    self.long_opts[-1] = long # XXX redundant?!
                self.takes_arg[long] = 0

            # If this jest an alias option, make sure its "takes arg" flag jest
            # the same jako the option it's aliased to.
            alias_to = self.alias.get(long)
            jeżeli alias_to jest nie Nic:
                jeżeli self.takes_arg[long] != self.takes_arg[alias_to]:
                    podnieś DistutilsGetoptError(
                          "invalid alias '%s': inconsistent przy "
                          "aliased option '%s' (one of them takes a value, "
                          "the other doesn't"
                          % (long, alias_to))

            # Now enforce some bondage on the long option name, so we can
            # later translate it to an attribute name on some object.  Have
            # to do this a bit late to make sure we've removed any trailing
            # '='.
            jeżeli nie longopt_re.match(long):
                podnieś DistutilsGetoptError(
                       "invalid long option name '%s' "
                       "(must be letters, numbers, hyphens only" % long)

            self.attr_name[long] = self.get_attr_name(long)
            jeżeli short:
                self.short_opts.append(short)
                self.short2long[short[0]] = long

    def getopt(self, args=Nic, object=Nic):
        """Parse command-line options w args. Store jako attributes on object.

        If 'args' jest Nic albo nie supplied, uses 'sys.argv[1:]'.  If
        'object' jest Nic albo nie supplied, creates a new OptionDummy
        object, stores option values there, oraz returns a tuple (args,
        object).  If 'object' jest supplied, it jest modified w place oraz
        'getopt()' just returns 'args'; w both cases, the returned
        'args' jest a modified copy of the dalejed-in 'args' list, which
        jest left untouched.
        """
        jeżeli args jest Nic:
            args = sys.argv[1:]
        jeżeli object jest Nic:
            object = OptionDummy()
            created_object = Prawda
        inaczej:
            created_object = Nieprawda

        self._grok_option_table()

        short_opts = ' '.join(self.short_opts)
        spróbuj:
            opts, args = getopt.getopt(args, short_opts, self.long_opts)
        wyjąwszy getopt.error jako msg:
            podnieś DistutilsArgError(msg)

        dla opt, val w opts:
            jeżeli len(opt) == 2 oraz opt[0] == '-': # it's a short option
                opt = self.short2long[opt[1]]
            inaczej:
                assert len(opt) > 2 oraz opt[:2] == '--'
                opt = opt[2:]

            alias = self.alias.get(opt)
            jeżeli alias:
                opt = alias

            jeżeli nie self.takes_arg[opt]:     # boolean option?
                assert val == '', "boolean option can't have value"
                alias = self.negative_alias.get(opt)
                jeżeli alias:
                    opt = alias
                    val = 0
                inaczej:
                    val = 1

            attr = self.attr_name[opt]
            # The only repeating option at the moment jest 'verbose'.
            # It has a negative option -q quiet, which should set verbose = 0.
            jeżeli val oraz self.repeat.get(attr) jest nie Nic:
                val = getattr(object, attr, 0) + 1
            setattr(object, attr, val)
            self.option_order.append((opt, val))

        # dla opts
        jeżeli created_object:
            zwróć args, object
        inaczej:
            zwróć args

    def get_option_order(self):
        """Returns the list of (option, value) tuples processed by the
        previous run of 'getopt()'.  Raises RuntimeError if
        'getopt()' hasn't been called yet.
        """
        jeżeli self.option_order jest Nic:
            podnieś RuntimeError("'getopt()' hasn't been called yet")
        inaczej:
            zwróć self.option_order

    def generate_help(self, header=Nic):
        """Generate help text (a list of strings, one per suggested line of
        output) z the option table dla this FancyGetopt object.
        """
        # Blithely assume the option table jest good: probably wouldn't call
        # 'generate_help()' unless you've already called 'getopt()'.

        # First dalej: determine maximum length of long option names
        max_opt = 0
        dla option w self.option_table:
            long = option[0]
            short = option[1]
            l = len(long)
            jeżeli long[-1] == '=':
                l = l - 1
            jeżeli short jest nie Nic:
                l = l + 5                   # " (-x)" where short == 'x'
            jeżeli l > max_opt:
                max_opt = l

        opt_width = max_opt + 2 + 2 + 2     # room dla indent + dashes + gutter

        # Typical help block looks like this:
        #   --foo       controls foonabulation
        # Help block dla longest option looks like this:
        #   --flimflam  set the flim-flam level
        # oraz przy wrapped text:
        #   --flimflam  set the flim-flam level (must be between
        #               0 oraz 100, wyjąwszy on Tuesdays)
        # Options przy short names will have the short name shown (but
        # it doesn't contribute to max_opt):
        #   --foo (-f)  controls foonabulation
        # If adding the short option would make the left column too wide,
        # we push the explanation off to the next line
        #   --flimflam (-l)
        #               set the flim-flam level
        # Important parameters:
        #   - 2 spaces before option block start lines
        #   - 2 dashes dla each long option name
        #   - min. 2 spaces between option oraz explanation (gutter)
        #   - 5 characters (incl. space) dla short option name

        # Now generate lines of help text.  (If 80 columns were good enough
        # dla Jesus, then 78 columns are good enough dla me!)
        line_width = 78
        text_width = line_width - opt_width
        big_indent = ' ' * opt_width
        jeżeli header:
            lines = [header]
        inaczej:
            lines = ['Option summary:']

        dla option w self.option_table:
            long, short, help = option[:3]
            text = wrap_text(help, text_width)
            jeżeli long[-1] == '=':
                long = long[0:-1]

            # Case 1: no short option at all (makes life easy)
            jeżeli short jest Nic:
                jeżeli text:
                    lines.append("  --%-*s  %s" % (max_opt, long, text[0]))
                inaczej:
                    lines.append("  --%-*s  " % (max_opt, long))

            # Case 2: we have a short option, so we have to include it
            # just after the long option
            inaczej:
                opt_names = "%s (-%s)" % (long, short)
                jeżeli text:
                    lines.append("  --%-*s  %s" %
                                 (max_opt, opt_names, text[0]))
                inaczej:
                    lines.append("  --%-*s" % opt_names)

            dla l w text[1:]:
                lines.append(big_indent + l)
        zwróć lines

    def print_help(self, header=Nic, file=Nic):
        jeżeli file jest Nic:
            file = sys.stdout
        dla line w self.generate_help(header):
            file.write(line + "\n")


def fancy_getopt(options, negative_opt, object, args):
    parser = FancyGetopt(options)
    parser.set_negative_aliases(negative_opt)
    zwróć parser.getopt(args, object)


WS_TRANS = {ord(_wschar) : ' ' dla _wschar w string.whitespace}

def wrap_text(text, width):
    """wrap_text(text : string, width : int) -> [string]

    Split 'text' into multiple lines of no more than 'width' characters
    each, oraz zwróć the list of strings that results.
    """
    jeżeli text jest Nic:
        zwróć []
    jeżeli len(text) <= width:
        zwróć [text]

    text = text.expandtabs()
    text = text.translate(WS_TRANS)
    chunks = re.split(r'( +|-+)', text)
    chunks = [ch dla ch w chunks jeżeli ch] # ' - ' results w empty strings
    lines = []

    dopóki chunks:
        cur_line = []                   # list of chunks (to-be-joined)
        cur_len = 0                     # length of current line

        dopóki chunks:
            l = len(chunks[0])
            jeżeli cur_len + l <= width:    # can squeeze (at least) this chunk w
                cur_line.append(chunks[0])
                usuń chunks[0]
                cur_len = cur_len + l
            inaczej:                       # this line jest full
                # drop last chunk jeżeli all space
                jeżeli cur_line oraz cur_line[-1][0] == ' ':
                    usuń cur_line[-1]
                przerwij

        jeżeli chunks:                      # any chunks left to process?
            # jeżeli the current line jest still empty, then we had a single
            # chunk that's too big too fit on a line -- so we przerwij
            # down oraz przerwij it up at the line width
            jeżeli cur_len == 0:
                cur_line.append(chunks[0][0:width])
                chunks[0] = chunks[0][width:]

            # all-whitespace chunks at the end of a line can be discarded
            # (and we know z the re.split above that jeżeli a chunk has
            # *any* whitespace, it jest *all* whitespace)
            jeżeli chunks[0][0] == ' ':
                usuń chunks[0]

        # oraz store this line w the list-of-all-lines -- jako a single
        # string, of course!
        lines.append(''.join(cur_line))

    zwróć lines


def translate_longopt(opt):
    """Convert a long option name to a valid Python identifier by
    changing "-" to "_".
    """
    zwróć opt.translate(longopt_xlate)


klasa OptionDummy:
    """Dummy klasa just used jako a place to hold command-line option
    values jako instance attributes."""

    def __init__(self, options=[]):
        """Create a new OptionDummy instance.  The attributes listed w
        'options' will be initialized to Nic."""
        dla opt w options:
            setattr(self, opt, Nic)


jeżeli __name__ == "__main__":
    text = """\
Tra-la-la, supercalifragilisticexpialidocious.
How *do* you spell that odd word, anyways?
(Someone ask Mary -- she'll know [or she'll
say, "How should I know?"].)"""

    dla ww w (10, 20, 30, 40):
        print("width: %d" % ww)
        print("\n".join(wrap_text(text, ww)))
        print()
