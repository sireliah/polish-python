"""A powerful, extensible, oraz easy-to-use option parser.

By Greg Ward <gward@python.net>

Originally distributed jako Optik.

For support, use the optik-users@lists.sourceforge.net mailing list
(http://lists.sourceforge.net/lists/listinfo/optik-users).

Simple usage example:

   z optparse zaimportuj OptionParser

   parser = OptionParser()
   parser.add_option("-f", "--file", dest="filename",
                     help="write report to FILE", metavar="FILE")
   parser.add_option("-q", "--quiet",
                     action="store_false", dest="verbose", default=Prawda,
                     help="don't print status messages to stdout")

   (options, args) = parser.parse_args()
"""

__version__ = "1.5.3"

__all__ = ['Option',
           'make_option',
           'SUPPRESS_HELP',
           'SUPPRESS_USAGE',
           'Values',
           'OptionContainer',
           'OptionGroup',
           'OptionParser',
           'HelpFormatter',
           'IndentedHelpFormatter',
           'TitledHelpFormatter',
           'OptParseError',
           'OptionError',
           'OptionConflictError',
           'OptionValueError',
           'BadOptionError']

__copyright__ = """
Copyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.
Copyright (c) 2002-2006 Python Software Foundation.  All rights reserved.

Redistribution oraz use w source oraz binary forms, przy albo without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions oraz the following disclaimer.

  * Redistributions w binary form must reproduce the above copyright
    notice, this list of conditions oraz the following disclaimer w the
    documentation and/or other materials provided przy the distribution.

  * Neither the name of the author nor the names of its
    contributors may be used to endorse albo promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

zaimportuj sys, os
zaimportuj textwrap

def _repr(self):
    zwróć "<%s at 0x%x: %s>" % (self.__class__.__name__, id(self), self)


# This file was generated from:
#   Id: option_parser.py 527 2006-07-23 15:21:30Z greg
#   Id: option.py 522 2006-06-11 16:22:03Z gward
#   Id: help.py 527 2006-07-23 15:21:30Z greg
#   Id: errors.py 509 2006-04-20 00:58:24Z gward

spróbuj:
    z gettext zaimportuj gettext, ngettext
wyjąwszy ImportError:
    def gettext(message):
        zwróć message

    def ngettext(singular, plural, n):
        jeżeli n == 1:
            zwróć singular
        zwróć plural

_ = gettext


klasa OptParseError (Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        zwróć self.msg


klasa OptionError (OptParseError):
    """
    Raised jeżeli an Option instance jest created przy invalid albo
    inconsistent arguments.
    """

    def __init__(self, msg, option):
        self.msg = msg
        self.option_id = str(option)

    def __str__(self):
        jeżeli self.option_id:
            zwróć "option %s: %s" % (self.option_id, self.msg)
        inaczej:
            zwróć self.msg

klasa OptionConflictError (OptionError):
    """
    Raised jeżeli conflicting options are added to an OptionParser.
    """

klasa OptionValueError (OptParseError):
    """
    Raised jeżeli an invalid option value jest encountered on the command
    line.
    """

klasa BadOptionError (OptParseError):
    """
    Raised jeżeli an invalid option jest seen on the command line.
    """
    def __init__(self, opt_str):
        self.opt_str = opt_str

    def __str__(self):
        zwróć _("no such option: %s") % self.opt_str

klasa AmbiguousOptionError (BadOptionError):
    """
    Raised jeżeli an ambiguous option jest seen on the command line.
    """
    def __init__(self, opt_str, possibilities):
        BadOptionError.__init__(self, opt_str)
        self.possibilities = possibilities

    def __str__(self):
        zwróć (_("ambiguous option: %s (%s?)")
                % (self.opt_str, ", ".join(self.possibilities)))


klasa HelpFormatter:

    """
    Abstract base klasa dla formatting option help.  OptionParser
    instances should use one of the HelpFormatter subclasses for
    formatting help; by default IndentedHelpFormatter jest used.

    Instance attributes:
      parser : OptionParser
        the controlling OptionParser instance
      indent_increment : int
        the number of columns to indent per nesting level
      max_help_position : int
        the maximum starting column dla option help text
      help_position : int
        the calculated starting column dla option help text;
        initially the same jako the maximum
      width : int
        total number of columns dla output (pass Nic to constructor for
        this value to be taken z the $COLUMNS environment variable)
      level : int
        current indentation level
      current_indent : int
        current indentation level (in columns)
      help_width : int
        number of columns available dla option help text (calculated)
      default_tag : str
        text to replace przy each option's default value, "%default"
        by default.  Set to false value to disable default value expansion.
      option_strings : { Option : str }
        maps Option instances to the snippet of help text explaining
        the syntax of that option, e.g. "-h, --help" albo
        "-fFILE, --file=FILE"
      _short_opt_fmt : str
        format string controlling how short options przy values are
        printed w help text.  Must be either "%s%s" ("-fFILE") albo
        "%s %s" ("-f FILE"), because those are the two syntaxes that
        Optik supports.
      _long_opt_fmt : str
        similar but dla long options; must be either "%s %s" ("--file FILE")
        albo "%s=%s" ("--file=FILE").
    """

    NO_DEFAULT_VALUE = "none"

    def __init__(self,
                 indent_increment,
                 max_help_position,
                 width,
                 short_first):
        self.parser = Nic
        self.indent_increment = indent_increment
        jeżeli width jest Nic:
            spróbuj:
                width = int(os.environ['COLUMNS'])
            wyjąwszy (KeyError, ValueError):
                width = 80
            width -= 2
        self.width = width
        self.help_position = self.max_help_position = \
                min(max_help_position, max(width - 20, indent_increment * 2))
        self.current_indent = 0
        self.level = 0
        self.help_width = Nic          # computed later
        self.short_first = short_first
        self.default_tag = "%default"
        self.option_strings = {}
        self._short_opt_fmt = "%s %s"
        self._long_opt_fmt = "%s=%s"

    def set_parser(self, parser):
        self.parser = parser

    def set_short_opt_delimiter(self, delim):
        jeżeli delim nie w ("", " "):
            podnieś ValueError(
                "invalid metavar delimiter dla short options: %r" % delim)
        self._short_opt_fmt = "%s" + delim + "%s"

    def set_long_opt_delimiter(self, delim):
        jeżeli delim nie w ("=", " "):
            podnieś ValueError(
                "invalid metavar delimiter dla long options: %r" % delim)
        self._long_opt_fmt = "%s" + delim + "%s"

    def indent(self):
        self.current_indent += self.indent_increment
        self.level += 1

    def dedent(self):
        self.current_indent -= self.indent_increment
        assert self.current_indent >= 0, "Indent decreased below 0."
        self.level -= 1

    def format_usage(self, usage):
        podnieś NotImplementedError("subclasses must implement")

    def format_heading(self, heading):
        podnieś NotImplementedError("subclasses must implement")

    def _format_text(self, text):
        """
        Format a paragraph of free-form text dla inclusion w the
        help output at the current indentation level.
        """
        text_width = max(self.width - self.current_indent, 11)
        indent = " "*self.current_indent
        zwróć textwrap.fill(text,
                             text_width,
                             initial_indent=indent,
                             subsequent_indent=indent)

    def format_description(self, description):
        jeżeli description:
            zwróć self._format_text(description) + "\n"
        inaczej:
            zwróć ""

    def format_epilog(self, epilog):
        jeżeli epilog:
            zwróć "\n" + self._format_text(epilog) + "\n"
        inaczej:
            zwróć ""


    def expand_default(self, option):
        jeżeli self.parser jest Nic albo nie self.default_tag:
            zwróć option.help

        default_value = self.parser.defaults.get(option.dest)
        jeżeli default_value jest NO_DEFAULT albo default_value jest Nic:
            default_value = self.NO_DEFAULT_VALUE

        zwróć option.help.replace(self.default_tag, str(default_value))

    def format_option(self, option):
        # The help dla each option consists of two parts:
        #   * the opt strings oraz metavars
        #     eg. ("-x", albo "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #     eg. ("turn on expert mode", "read data z FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x      turn on expert mode
        #
        # But jeżeli the opt string list jest too long, we put the help
        # string on a second line, indented to the same column it would
        # start w jeżeli it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #           read data z FILENAME
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        jeżeli len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        inaczej:                       # start help on same line jako opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        jeżeli option.help:
            help_text = self.expand_default(option)
            help_lines = textwrap.wrap(help_text, self.help_width)
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           dla line w help_lines[1:]])
        albo_inaczej opts[-1] != "\n":
            result.append("\n")
        zwróć "".join(result)

    def store_option_strings(self, parser):
        self.indent()
        max_len = 0
        dla opt w parser.option_list:
            strings = self.format_option_strings(opt)
            self.option_strings[opt] = strings
            max_len = max(max_len, len(strings) + self.current_indent)
        self.indent()
        dla group w parser.option_groups:
            dla opt w group.option_list:
                strings = self.format_option_strings(opt)
                self.option_strings[opt] = strings
                max_len = max(max_len, len(strings) + self.current_indent)
        self.dedent()
        self.dedent()
        self.help_position = min(max_len + 2, self.max_help_position)
        self.help_width = max(self.width - self.help_position, 11)

    def format_option_strings(self, option):
        """Return a comma-separated list of option strings & metavariables."""
        jeżeli option.takes_value():
            metavar = option.metavar albo option.dest.upper()
            short_opts = [self._short_opt_fmt % (sopt, metavar)
                          dla sopt w option._short_opts]
            long_opts = [self._long_opt_fmt % (lopt, metavar)
                         dla lopt w option._long_opts]
        inaczej:
            short_opts = option._short_opts
            long_opts = option._long_opts

        jeżeli self.short_first:
            opts = short_opts + long_opts
        inaczej:
            opts = long_opts + short_opts

        zwróć ", ".join(opts)

klasa IndentedHelpFormatter (HelpFormatter):
    """Format help przy indented section bodies.
    """

    def __init__(self,
                 indent_increment=2,
                 max_help_position=24,
                 width=Nic,
                 short_first=1):
        HelpFormatter.__init__(
            self, indent_increment, max_help_position, width, short_first)

    def format_usage(self, usage):
        zwróć _("Usage: %s\n") % usage

    def format_heading(self, heading):
        zwróć "%*s%s:\n" % (self.current_indent, "", heading)


klasa TitledHelpFormatter (HelpFormatter):
    """Format help przy underlined section headers.
    """

    def __init__(self,
                 indent_increment=0,
                 max_help_position=24,
                 width=Nic,
                 short_first=0):
        HelpFormatter.__init__ (
            self, indent_increment, max_help_position, width, short_first)

    def format_usage(self, usage):
        zwróć "%s  %s\n" % (self.format_heading(_("Usage")), usage)

    def format_heading(self, heading):
        zwróć "%s\n%s\n" % (heading, "=-"[self.level] * len(heading))


def _parse_num(val, type):
    jeżeli val[:2].lower() == "0x":         # hexadecimal
        radix = 16
    albo_inaczej val[:2].lower() == "0b":       # binary
        radix = 2
        val = val[2:] albo "0"            # have to remove "0b" prefix
    albo_inaczej val[:1] == "0":                # octal
        radix = 8
    inaczej:                               # decimal
        radix = 10

    zwróć type(val, radix)

def _parse_int(val):
    zwróć _parse_num(val, int)

_builtin_cvt = { "int" : (_parse_int, _("integer")),
                 "long" : (_parse_int, _("integer")),
                 "float" : (float, _("floating-point")),
                 "complex" : (complex, _("complex")) }

def check_builtin(option, opt, value):
    (cvt, what) = _builtin_cvt[option.type]
    spróbuj:
        zwróć cvt(value)
    wyjąwszy ValueError:
        podnieś OptionValueError(
            _("option %s: invalid %s value: %r") % (opt, what, value))

def check_choice(option, opt, value):
    jeżeli value w option.choices:
        zwróć value
    inaczej:
        choices = ", ".join(map(repr, option.choices))
        podnieś OptionValueError(
            _("option %s: invalid choice: %r (choose z %s)")
            % (opt, value, choices))

# Not supplying a default jest different z a default of Nic,
# so we need an explicit "not supplied" value.
NO_DEFAULT = ("NO", "DEFAULT")


klasa Option:
    """
    Instance attributes:
      _short_opts : [string]
      _long_opts : [string]

      action : string
      type : string
      dest : string
      default : any
      nargs : int
      const : any
      choices : [string]
      callback : function
      callback_args : (any*)
      callback_kwargs : { string : any }
      help : string
      metavar : string
    """

    # The list of instance attributes that may be set through
    # keyword args to the constructor.
    ATTRS = ['action',
             'type',
             'dest',
             'default',
             'nargs',
             'const',
             'choices',
             'callback',
             'callback_args',
             'callback_kwargs',
             'help',
             'metavar']

    # The set of actions allowed by option parsers.  Explicitly listed
    # here so the constructor can validate its arguments.
    ACTIONS = ("store",
               "store_const",
               "store_true",
               "store_false",
               "append",
               "append_const",
               "count",
               "callback",
               "help",
               "version")

    # The set of actions that involve storing a value somewhere;
    # also listed just dla constructor argument validation.  (If
    # the action jest one of these, there must be a destination.)
    STORE_ACTIONS = ("store",
                     "store_const",
                     "store_true",
                     "store_false",
                     "append",
                     "append_const",
                     "count")

    # The set of actions dla which it makes sense to supply a value
    # type, ie. which may consume an argument z the command line.
    TYPED_ACTIONS = ("store",
                     "append",
                     "callback")

    # The set of actions which *require* a value type, ie. that
    # always consume an argument z the command line.
    ALWAYS_TYPED_ACTIONS = ("store",
                            "append")

    # The set of actions which take a 'const' attribute.
    CONST_ACTIONS = ("store_const",
                     "append_const")

    # The set of known types dla option parsers.  Again, listed here for
    # constructor argument validation.
    TYPES = ("string", "int", "long", "float", "complex", "choice")

    # Dictionary of argument checking functions, which convert oraz
    # validate option arguments according to the option type.
    #
    # Signature of checking functions is:
    #   check(option : Option, opt : string, value : string) -> any
    # where
    #   option jest the Option instance calling the checker
    #   opt jest the actual option seen on the command-line
    #     (eg. "-a", "--file")
    #   value jest the option argument seen on the command-line
    #
    # The zwróć value should be w the appropriate Python type
    # dla option.type -- eg. an integer jeżeli option.type == "int".
    #
    # If no checker jest defined dla a type, arguments will be
    # unchecked oraz remain strings.
    TYPE_CHECKER = { "int"    : check_builtin,
                     "long"   : check_builtin,
                     "float"  : check_builtin,
                     "complex": check_builtin,
                     "choice" : check_choice,
                   }


    # CHECK_METHODS jest a list of unbound method objects; they are called
    # by the constructor, w order, after all attributes are
    # initialized.  The list jest created oraz filled w later, after all
    # the methods are actually defined.  (I just put it here because I
    # like to define oraz document all klasa attributes w the same
    # place.)  Subclasses that add another _check_*() method should
    # define their own CHECK_METHODS list that adds their check method
    # to those z this class.
    CHECK_METHODS = Nic


    # -- Constructor/initialization methods ----------------------------

    def __init__(self, *opts, **attrs):
        # Set _short_opts, _long_opts attrs z 'opts' tuple.
        # Have to be set now, w case no option strings are supplied.
        self._short_opts = []
        self._long_opts = []
        opts = self._check_opt_strings(opts)
        self._set_opt_strings(opts)

        # Set all other attrs (action, type, etc.) z 'attrs' dict
        self._set_attrs(attrs)

        # Check all the attributes we just set.  There are lots of
        # complicated interdependencies, but luckily they can be farmed
        # out to the _check_*() methods listed w CHECK_METHODS -- which
        # could be handy dla subclasses!  The one thing these all share
        # jest that they podnieś OptionError jeżeli they discover a problem.
        dla checker w self.CHECK_METHODS:
            checker(self)

    def _check_opt_strings(self, opts):
        # Filter out Nic because early versions of Optik had exactly
        # one short option oraz one long option, either of which
        # could be Nic.
        opts = [opt dla opt w opts jeżeli opt]
        jeżeli nie opts:
            podnieś TypeError("at least one option string must be supplied")
        zwróć opts

    def _set_opt_strings(self, opts):
        dla opt w opts:
            jeżeli len(opt) < 2:
                podnieś OptionError(
                    "invalid option string %r: "
                    "must be at least two characters long" % opt, self)
            albo_inaczej len(opt) == 2:
                jeżeli nie (opt[0] == "-" oraz opt[1] != "-"):
                    podnieś OptionError(
                        "invalid short option string %r: "
                        "must be of the form -x, (x any non-dash char)" % opt,
                        self)
                self._short_opts.append(opt)
            inaczej:
                jeżeli nie (opt[0:2] == "--" oraz opt[2] != "-"):
                    podnieś OptionError(
                        "invalid long option string %r: "
                        "must start przy --, followed by non-dash" % opt,
                        self)
                self._long_opts.append(opt)

    def _set_attrs(self, attrs):
        dla attr w self.ATTRS:
            jeżeli attr w attrs:
                setattr(self, attr, attrs[attr])
                usuń attrs[attr]
            inaczej:
                jeżeli attr == 'default':
                    setattr(self, attr, NO_DEFAULT)
                inaczej:
                    setattr(self, attr, Nic)
        jeżeli attrs:
            attrs = sorted(attrs.keys())
            podnieś OptionError(
                "invalid keyword arguments: %s" % ", ".join(attrs),
                self)


    # -- Constructor validation methods --------------------------------

    def _check_action(self):
        jeżeli self.action jest Nic:
            self.action = "store"
        albo_inaczej self.action nie w self.ACTIONS:
            podnieś OptionError("invalid action: %r" % self.action, self)

    def _check_type(self):
        jeżeli self.type jest Nic:
            jeżeli self.action w self.ALWAYS_TYPED_ACTIONS:
                jeżeli self.choices jest nie Nic:
                    # The "choices" attribute implies "choice" type.
                    self.type = "choice"
                inaczej:
                    # No type given?  "string" jest the most sensible default.
                    self.type = "string"
        inaczej:
            # Allow type objects albo builtin type conversion functions
            # (int, str, etc.) jako an alternative to their names.
            jeżeli isinstance(self.type, type):
                self.type = self.type.__name__

            jeżeli self.type == "str":
                self.type = "string"

            jeżeli self.type nie w self.TYPES:
                podnieś OptionError("invalid option type: %r" % self.type, self)
            jeżeli self.action nie w self.TYPED_ACTIONS:
                podnieś OptionError(
                    "must nie supply a type dla action %r" % self.action, self)

    def _check_choice(self):
        jeżeli self.type == "choice":
            jeżeli self.choices jest Nic:
                podnieś OptionError(
                    "must supply a list of choices dla type 'choice'", self)
            albo_inaczej nie isinstance(self.choices, (tuple, list)):
                podnieś OptionError(
                    "choices must be a list of strings ('%s' supplied)"
                    % str(type(self.choices)).split("'")[1], self)
        albo_inaczej self.choices jest nie Nic:
            podnieś OptionError(
                "must nie supply choices dla type %r" % self.type, self)

    def _check_dest(self):
        # No destination given, oraz we need one dla this action.  The
        # self.type check jest dla callbacks that take a value.
        takes_value = (self.action w self.STORE_ACTIONS albo
                       self.type jest nie Nic)
        jeżeli self.dest jest Nic oraz takes_value:

            # Glean a destination z the first long option string,
            # albo z the first short option string jeżeli no long options.
            jeżeli self._long_opts:
                # eg. "--foo-bar" -> "foo_bar"
                self.dest = self._long_opts[0][2:].replace('-', '_')
            inaczej:
                self.dest = self._short_opts[0][1]

    def _check_const(self):
        jeżeli self.action nie w self.CONST_ACTIONS oraz self.const jest nie Nic:
            podnieś OptionError(
                "'const' must nie be supplied dla action %r" % self.action,
                self)

    def _check_nargs(self):
        jeżeli self.action w self.TYPED_ACTIONS:
            jeżeli self.nargs jest Nic:
                self.nargs = 1
        albo_inaczej self.nargs jest nie Nic:
            podnieś OptionError(
                "'nargs' must nie be supplied dla action %r" % self.action,
                self)

    def _check_callback(self):
        jeżeli self.action == "callback":
            jeżeli nie callable(self.callback):
                podnieś OptionError(
                    "callback nie callable: %r" % self.callback, self)
            jeżeli (self.callback_args jest nie Nic oraz
                nie isinstance(self.callback_args, tuple)):
                podnieś OptionError(
                    "callback_args, jeżeli supplied, must be a tuple: nie %r"
                    % self.callback_args, self)
            jeżeli (self.callback_kwargs jest nie Nic oraz
                nie isinstance(self.callback_kwargs, dict)):
                podnieś OptionError(
                    "callback_kwargs, jeżeli supplied, must be a dict: nie %r"
                    % self.callback_kwargs, self)
        inaczej:
            jeżeli self.callback jest nie Nic:
                podnieś OptionError(
                    "callback supplied (%r) dla non-callback option"
                    % self.callback, self)
            jeżeli self.callback_args jest nie Nic:
                podnieś OptionError(
                    "callback_args supplied dla non-callback option", self)
            jeżeli self.callback_kwargs jest nie Nic:
                podnieś OptionError(
                    "callback_kwargs supplied dla non-callback option", self)


    CHECK_METHODS = [_check_action,
                     _check_type,
                     _check_choice,
                     _check_dest,
                     _check_const,
                     _check_nargs,
                     _check_callback]


    # -- Miscellaneous methods -----------------------------------------

    def __str__(self):
        zwróć "/".join(self._short_opts + self._long_opts)

    __repr__ = _repr

    def takes_value(self):
        zwróć self.type jest nie Nic

    def get_opt_string(self):
        jeżeli self._long_opts:
            zwróć self._long_opts[0]
        inaczej:
            zwróć self._short_opts[0]


    # -- Processing methods --------------------------------------------

    def check_value(self, opt, value):
        checker = self.TYPE_CHECKER.get(self.type)
        jeżeli checker jest Nic:
            zwróć value
        inaczej:
            zwróć checker(self, opt, value)

    def convert_value(self, opt, value):
        jeżeli value jest nie Nic:
            jeżeli self.nargs == 1:
                zwróć self.check_value(opt, value)
            inaczej:
                zwróć tuple([self.check_value(opt, v) dla v w value])

    def process(self, opt, value, values, parser):

        # First, convert the value(s) to the right type.  Howl jeżeli any
        # value(s) are bogus.
        value = self.convert_value(opt, value)

        # And then take whatever action jest expected of us.
        # This jest a separate method to make life easier for
        # subclasses to add new actions.
        zwróć self.take_action(
            self.action, self.dest, opt, value, values, parser)

    def take_action(self, action, dest, opt, value, values, parser):
        jeżeli action == "store":
            setattr(values, dest, value)
        albo_inaczej action == "store_const":
            setattr(values, dest, self.const)
        albo_inaczej action == "store_true":
            setattr(values, dest, Prawda)
        albo_inaczej action == "store_false":
            setattr(values, dest, Nieprawda)
        albo_inaczej action == "append":
            values.ensure_value(dest, []).append(value)
        albo_inaczej action == "append_const":
            values.ensure_value(dest, []).append(self.const)
        albo_inaczej action == "count":
            setattr(values, dest, values.ensure_value(dest, 0) + 1)
        albo_inaczej action == "callback":
            args = self.callback_args albo ()
            kwargs = self.callback_kwargs albo {}
            self.callback(self, opt, value, parser, *args, **kwargs)
        albo_inaczej action == "help":
            parser.print_help()
            parser.exit()
        albo_inaczej action == "version":
            parser.print_version()
            parser.exit()
        inaczej:
            podnieś ValueError("unknown action %r" % self.action)

        zwróć 1

# klasa Option


SUPPRESS_HELP = "SUPPRESS"+"HELP"
SUPPRESS_USAGE = "SUPPRESS"+"USAGE"

klasa Values:

    def __init__(self, defaults=Nic):
        jeżeli defaults:
            dla (attr, val) w defaults.items():
                setattr(self, attr, val)

    def __str__(self):
        zwróć str(self.__dict__)

    __repr__ = _repr

    def __eq__(self, other):
        jeżeli isinstance(other, Values):
            zwróć self.__dict__ == other.__dict__
        albo_inaczej isinstance(other, dict):
            zwróć self.__dict__ == other
        inaczej:
            zwróć NotImplemented

    def _update_careful(self, dict):
        """
        Update the option values z an arbitrary dictionary, but only
        use keys z dict that already have a corresponding attribute
        w self.  Any keys w dict without a corresponding attribute
        are silently ignored.
        """
        dla attr w dir(self):
            jeżeli attr w dict:
                dval = dict[attr]
                jeżeli dval jest nie Nic:
                    setattr(self, attr, dval)

    def _update_loose(self, dict):
        """
        Update the option values z an arbitrary dictionary,
        using all keys z the dictionary regardless of whether
        they have a corresponding attribute w self albo not.
        """
        self.__dict__.update(dict)

    def _update(self, dict, mode):
        jeżeli mode == "careful":
            self._update_careful(dict)
        albo_inaczej mode == "loose":
            self._update_loose(dict)
        inaczej:
            podnieś ValueError("invalid update mode: %r" % mode)

    def read_module(self, modname, mode="careful"):
        __import__(modname)
        mod = sys.modules[modname]
        self._update(vars(mod), mode)

    def read_file(self, filename, mode="careful"):
        vars = {}
        exec(open(filename).read(), vars)
        self._update(vars, mode)

    def ensure_value(self, attr, value):
        jeżeli nie hasattr(self, attr) albo getattr(self, attr) jest Nic:
            setattr(self, attr, value)
        zwróć getattr(self, attr)


klasa OptionContainer:

    """
    Abstract base class.

    Class attributes:
      standard_option_list : [Option]
        list of standard options that will be accepted by all instances
        of this parser klasa (intended to be overridden by subclasses).

    Instance attributes:
      option_list : [Option]
        the list of Option objects contained by this OptionContainer
      _short_opt : { string : Option }
        dictionary mapping short option strings, eg. "-f" albo "-X",
        to the Option instances that implement them.  If an Option
        has multiple short option strings, it will appears w this
        dictionary multiple times. [1]
      _long_opt : { string : Option }
        dictionary mapping long option strings, eg. "--file" albo
        "--exclude", to the Option instances that implement them.
        Again, a given Option can occur multiple times w this
        dictionary. [1]
      defaults : { string : any }
        dictionary mapping option destination names to default
        values dla each destination [1]

    [1] These mappings are common to (shared by) all components of the
        controlling OptionParser, where they are initially created.

    """

    def __init__(self, option_class, conflict_handler, description):
        # Initialize the option list oraz related data structures.
        # This method must be provided by subclasses, oraz it must
        # initialize at least the following instance attributes:
        # option_list, _short_opt, _long_opt, defaults.
        self._create_option_list()

        self.option_class = option_class
        self.set_conflict_handler(conflict_handler)
        self.set_description(description)

    def _create_option_mappings(self):
        # For use by OptionParser constructor -- create the master
        # option mappings used by this OptionParser oraz all
        # OptionGroups that it owns.
        self._short_opt = {}            # single letter -> Option instance
        self._long_opt = {}             # long option -> Option instance
        self.defaults = {}              # maps option dest -> default value


    def _share_option_mappings(self, parser):
        # For use by OptionGroup constructor -- use shared option
        # mappings z the OptionParser that owns this OptionGroup.
        self._short_opt = parser._short_opt
        self._long_opt = parser._long_opt
        self.defaults = parser.defaults

    def set_conflict_handler(self, handler):
        jeżeli handler nie w ("error", "resolve"):
            podnieś ValueError("invalid conflict_resolution value %r" % handler)
        self.conflict_handler = handler

    def set_description(self, description):
        self.description = description

    def get_description(self):
        zwróć self.description


    def destroy(self):
        """see OptionParser.destroy()."""
        usuń self._short_opt
        usuń self._long_opt
        usuń self.defaults


    # -- Option-adding methods -----------------------------------------

    def _check_conflict(self, option):
        conflict_opts = []
        dla opt w option._short_opts:
            jeżeli opt w self._short_opt:
                conflict_opts.append((opt, self._short_opt[opt]))
        dla opt w option._long_opts:
            jeżeli opt w self._long_opt:
                conflict_opts.append((opt, self._long_opt[opt]))

        jeżeli conflict_opts:
            handler = self.conflict_handler
            jeżeli handler == "error":
                podnieś OptionConflictError(
                    "conflicting option string(s): %s"
                    % ", ".join([co[0] dla co w conflict_opts]),
                    option)
            albo_inaczej handler == "resolve":
                dla (opt, c_option) w conflict_opts:
                    jeżeli opt.startswith("--"):
                        c_option._long_opts.remove(opt)
                        usuń self._long_opt[opt]
                    inaczej:
                        c_option._short_opts.remove(opt)
                        usuń self._short_opt[opt]
                    jeżeli nie (c_option._short_opts albo c_option._long_opts):
                        c_option.container.option_list.remove(c_option)

    def add_option(self, *args, **kwargs):
        """add_option(Option)
           add_option(opt_str, ..., kwarg=val, ...)
        """
        jeżeli isinstance(args[0], str):
            option = self.option_class(*args, **kwargs)
        albo_inaczej len(args) == 1 oraz nie kwargs:
            option = args[0]
            jeżeli nie isinstance(option, Option):
                podnieś TypeError("not an Option instance: %r" % option)
        inaczej:
            podnieś TypeError("invalid arguments")

        self._check_conflict(option)

        self.option_list.append(option)
        option.container = self
        dla opt w option._short_opts:
            self._short_opt[opt] = option
        dla opt w option._long_opts:
            self._long_opt[opt] = option

        jeżeli option.dest jest nie Nic:     # option has a dest, we need a default
            jeżeli option.default jest nie NO_DEFAULT:
                self.defaults[option.dest] = option.default
            albo_inaczej option.dest nie w self.defaults:
                self.defaults[option.dest] = Nic

        zwróć option

    def add_options(self, option_list):
        dla option w option_list:
            self.add_option(option)

    # -- Option query/removal methods ----------------------------------

    def get_option(self, opt_str):
        zwróć (self._short_opt.get(opt_str) albo
                self._long_opt.get(opt_str))

    def has_option(self, opt_str):
        zwróć (opt_str w self._short_opt albo
                opt_str w self._long_opt)

    def remove_option(self, opt_str):
        option = self._short_opt.get(opt_str)
        jeżeli option jest Nic:
            option = self._long_opt.get(opt_str)
        jeżeli option jest Nic:
            podnieś ValueError("no such option %r" % opt_str)

        dla opt w option._short_opts:
            usuń self._short_opt[opt]
        dla opt w option._long_opts:
            usuń self._long_opt[opt]
        option.container.option_list.remove(option)


    # -- Help-formatting methods ---------------------------------------

    def format_option_help(self, formatter):
        jeżeli nie self.option_list:
            zwróć ""
        result = []
        dla option w self.option_list:
            jeżeli nie option.help jest SUPPRESS_HELP:
                result.append(formatter.format_option(option))
        zwróć "".join(result)

    def format_description(self, formatter):
        zwróć formatter.format_description(self.get_description())

    def format_help(self, formatter):
        result = []
        jeżeli self.description:
            result.append(self.format_description(formatter))
        jeżeli self.option_list:
            result.append(self.format_option_help(formatter))
        zwróć "\n".join(result)


klasa OptionGroup (OptionContainer):

    def __init__(self, parser, title, description=Nic):
        self.parser = parser
        OptionContainer.__init__(
            self, parser.option_class, parser.conflict_handler, description)
        self.title = title

    def _create_option_list(self):
        self.option_list = []
        self._share_option_mappings(self.parser)

    def set_title(self, title):
        self.title = title

    def destroy(self):
        """see OptionParser.destroy()."""
        OptionContainer.destroy(self)
        usuń self.option_list

    # -- Help-formatting methods ---------------------------------------

    def format_help(self, formatter):
        result = formatter.format_heading(self.title)
        formatter.indent()
        result += OptionContainer.format_help(self, formatter)
        formatter.dedent()
        zwróć result


klasa OptionParser (OptionContainer):

    """
    Class attributes:
      standard_option_list : [Option]
        list of standard options that will be accepted by all instances
        of this parser klasa (intended to be overridden by subclasses).

    Instance attributes:
      usage : string
        a usage string dla your program.  Before it jest displayed
        to the user, "%prog" will be expanded to the name of
        your program (self.prog albo os.path.basename(sys.argv[0])).
      prog : string
        the name of the current program (to override
        os.path.basename(sys.argv[0])).
      description : string
        A paragraph of text giving a brief overview of your program.
        optparse reformats this paragraph to fit the current terminal
        width oraz prints it when the user requests help (after usage,
        but before the list of options).
      epilog : string
        paragraph of help text to print after option help

      option_groups : [OptionGroup]
        list of option groups w this parser (option groups are
        irrelevant dla parsing the command-line, but very useful
        dla generating help)

      allow_interspersed_args : bool = true
        jeżeli true, positional arguments may be interspersed przy options.
        Assuming -a oraz -b each take a single argument, the command-line
          -ablah foo bar -bboo baz
        will be interpreted the same as
          -ablah -bboo -- foo bar baz
        If this flag were false, that command line would be interpreted as
          -ablah -- foo bar -bboo baz
        -- ie. we stop processing options jako soon jako we see the first
        non-option argument.  (This jest the tradition followed by
        Python's getopt module, Perl's Getopt::Std, oraz other argument-
        parsing libraries, but it jest generally annoying to users.)

      process_default_values : bool = true
        jeżeli true, option default values are processed similarly to option
        values z the command line: that is, they are dalejed to the
        type-checking function dla the option's type (as long jako the
        default value jest a string).  (This really only matters jeżeli you
        have defined custom types; see SF bug #955889.)  Set it to false
        to restore the behaviour of Optik 1.4.1 oraz earlier.

      rargs : [string]
        the argument list currently being parsed.  Only set when
        parse_args() jest active, oraz continually trimmed down as
        we consume arguments.  Mainly there dla the benefit of
        callback options.
      largs : [string]
        the list of leftover arguments that we have skipped while
        parsing options.  If allow_interspersed_args jest false, this
        list jest always empty.
      values : Values
        the set of option values currently being accumulated.  Only
        set when parse_args() jest active.  Also mainly dla callbacks.

    Because of the 'rargs', 'largs', oraz 'values' attributes,
    OptionParser jest nie thread-safe.  If, dla some perverse reason, you
    need to parse command-line arguments simultaneously w different
    threads, use different OptionParser instances.

    """

    standard_option_list = []

    def __init__(self,
                 usage=Nic,
                 option_list=Nic,
                 option_class=Option,
                 version=Nic,
                 conflict_handler="error",
                 description=Nic,
                 formatter=Nic,
                 add_help_option=Prawda,
                 prog=Nic,
                 epilog=Nic):
        OptionContainer.__init__(
            self, option_class, conflict_handler, description)
        self.set_usage(usage)
        self.prog = prog
        self.version = version
        self.allow_interspersed_args = Prawda
        self.process_default_values = Prawda
        jeżeli formatter jest Nic:
            formatter = IndentedHelpFormatter()
        self.formatter = formatter
        self.formatter.set_parser(self)
        self.epilog = epilog

        # Populate the option list; initial sources are the
        # standard_option_list klasa attribute, the 'option_list'
        # argument, oraz (jeżeli applicable) the _add_version_option() oraz
        # _add_help_option() methods.
        self._populate_option_list(option_list,
                                   add_help=add_help_option)

        self._init_parsing_state()


    def destroy(self):
        """
        Declare that you are done przy this OptionParser.  This cleans up
        reference cycles so the OptionParser (and all objects referenced by
        it) can be garbage-collected promptly.  After calling destroy(), the
        OptionParser jest unusable.
        """
        OptionContainer.destroy(self)
        dla group w self.option_groups:
            group.destroy()
        usuń self.option_list
        usuń self.option_groups
        usuń self.formatter


    # -- Private methods -----------------------------------------------
    # (used by our albo OptionContainer's constructor)

    def _create_option_list(self):
        self.option_list = []
        self.option_groups = []
        self._create_option_mappings()

    def _add_help_option(self):
        self.add_option("-h", "--help",
                        action="help",
                        help=_("show this help message oraz exit"))

    def _add_version_option(self):
        self.add_option("--version",
                        action="version",
                        help=_("show program's version number oraz exit"))

    def _populate_option_list(self, option_list, add_help=Prawda):
        jeżeli self.standard_option_list:
            self.add_options(self.standard_option_list)
        jeżeli option_list:
            self.add_options(option_list)
        jeżeli self.version:
            self._add_version_option()
        jeżeli add_help:
            self._add_help_option()

    def _init_parsing_state(self):
        # These are set w parse_args() dla the convenience of callbacks.
        self.rargs = Nic
        self.largs = Nic
        self.values = Nic


    # -- Simple modifier methods ---------------------------------------

    def set_usage(self, usage):
        jeżeli usage jest Nic:
            self.usage = _("%prog [options]")
        albo_inaczej usage jest SUPPRESS_USAGE:
            self.usage = Nic
        # For backwards compatibility przy Optik 1.3 oraz earlier.
        albo_inaczej usage.lower().startswith("usage: "):
            self.usage = usage[7:]
        inaczej:
            self.usage = usage

    def enable_interspersed_args(self):
        """Set parsing to nie stop on the first non-option, allowing
        interspersing switches przy command arguments. This jest the
        default behavior. See also disable_interspersed_args() oraz the
        klasa documentation description of the attribute
        allow_interspersed_args."""
        self.allow_interspersed_args = Prawda

    def disable_interspersed_args(self):
        """Set parsing to stop on the first non-option. Use this if
        you have a command processor which runs another command that
        has options of its own oraz you want to make sure these options
        don't get confused.
        """
        self.allow_interspersed_args = Nieprawda

    def set_process_default_values(self, process):
        self.process_default_values = process

    def set_default(self, dest, value):
        self.defaults[dest] = value

    def set_defaults(self, **kwargs):
        self.defaults.update(kwargs)

    def _get_all_options(self):
        options = self.option_list[:]
        dla group w self.option_groups:
            options.extend(group.option_list)
        zwróć options

    def get_default_values(self):
        jeżeli nie self.process_default_values:
            # Old, pre-Optik 1.5 behaviour.
            zwróć Values(self.defaults)

        defaults = self.defaults.copy()
        dla option w self._get_all_options():
            default = defaults.get(option.dest)
            jeżeli isinstance(default, str):
                opt_str = option.get_opt_string()
                defaults[option.dest] = option.check_value(opt_str, default)

        zwróć Values(defaults)


    # -- OptionGroup methods -------------------------------------------

    def add_option_group(self, *args, **kwargs):
        # XXX lots of overlap przy OptionContainer.add_option()
        jeżeli isinstance(args[0], str):
            group = OptionGroup(self, *args, **kwargs)
        albo_inaczej len(args) == 1 oraz nie kwargs:
            group = args[0]
            jeżeli nie isinstance(group, OptionGroup):
                podnieś TypeError("not an OptionGroup instance: %r" % group)
            jeżeli group.parser jest nie self:
                podnieś ValueError("invalid OptionGroup (wrong parser)")
        inaczej:
            podnieś TypeError("invalid arguments")

        self.option_groups.append(group)
        zwróć group

    def get_option_group(self, opt_str):
        option = (self._short_opt.get(opt_str) albo
                  self._long_opt.get(opt_str))
        jeżeli option oraz option.container jest nie self:
            zwróć option.container
        zwróć Nic


    # -- Option-parsing methods ----------------------------------------

    def _get_args(self, args):
        jeżeli args jest Nic:
            zwróć sys.argv[1:]
        inaczej:
            zwróć args[:]              # don't modify caller's list

    def parse_args(self, args=Nic, values=Nic):
        """
        parse_args(args : [string] = sys.argv[1:],
                   values : Values = Nic)
        -> (values : Values, args : [string])

        Parse the command-line options found w 'args' (default:
        sys.argv[1:]).  Any errors result w a call to 'error()', which
        by default prints the usage message to stderr oraz calls
        sys.exit() przy an error message.  On success returns a pair
        (values, args) where 'values' jest an Values instance (przy all
        your option values) oraz 'args' jest the list of arguments left
        over after parsing options.
        """
        rargs = self._get_args(args)
        jeżeli values jest Nic:
            values = self.get_default_values()

        # Store the halves of the argument list jako attributes dla the
        # convenience of callbacks:
        #   rargs
        #     the rest of the command-line (the "r" stands for
        #     "remaining" albo "right-hand")
        #   largs
        #     the leftover arguments -- ie. what's left after removing
        #     options oraz their arguments (the "l" stands dla "leftover"
        #     albo "left-hand")
        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        spróbuj:
            stop = self._process_args(largs, rargs, values)
        wyjąwszy (BadOptionError, OptionValueError) jako err:
            self.error(str(err))

        args = largs + rargs
        zwróć self.check_values(values, args)

    def check_values(self, values, args):
        """
        check_values(values : Values, args : [string])
        -> (values : Values, args : [string])

        Check that the supplied option values oraz leftover arguments are
        valid.  Returns the option values oraz leftover arguments
        (possibly adjusted, possibly completely new -- whatever you
        like).  Default implementation just returns the dalejed-in
        values; subclasses may override jako desired.
        """
        zwróć (values, args)

    def _process_args(self, largs, rargs, values):
        """_process_args(largs : [string],
                         rargs : [string],
                         values : Values)

        Process command-line arguments oraz populate 'values', consuming
        options oraz arguments z 'rargs'.  If 'allow_interspersed_args' jest
        false, stop at the first non-option argument.  If true, accumulate any
        interspersed non-option arguments w 'largs'.
        """
        dopóki rargs:
            arg = rargs[0]
            # We handle bare "--" explicitly, oraz bare "-" jest handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string jest greater than 1.
            jeżeli arg == "--":
                usuń rargs[0]
                zwróć
            albo_inaczej arg[0:2] == "--":
                # process a single long option (possibly przy value(s))
                self._process_long_opt(rargs, values)
            albo_inaczej arg[:1] == "-" oraz len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) dla the last one only)
                self._process_short_opts(rargs, values)
            albo_inaczej self.allow_interspersed_args:
                largs.append(arg)
                usuń rargs[0]
            inaczej:
                zwróć                  # stop now, leave this arg w rargs

        # Say this jest the original argument list:
        # [arg0, arg1, ..., arg(i-1), arg(i), arg(i+1), ..., arg(N-1)]
        #                            ^
        # (we are about to process arg(i)).
        #
        # Then rargs jest [arg(i), ..., arg(N-1)] oraz largs jest a *subset* of
        # [arg0, ..., arg(i-1)] (any options oraz their arguments will have
        # been removed z largs).
        #
        # The dopóki loop will usually consume 1 albo more arguments per dalej.
        # If it consumes 1 (eg. arg jest an option that takes no arguments),
        # then after _process_arg() jest done the situation is:
        #
        #   largs = subset of [arg0, ..., arg(i)]
        #   rargs = [arg(i+1), ..., arg(N-1)]
        #
        # If allow_interspersed_args jest false, largs will always be
        # *empty* -- still a subset of [arg0, ..., arg(i-1)], but
        # nie a very interesting subset!

    def _match_long_opt(self, opt):
        """_match_long_opt(opt : string) -> string

        Determine which long option string 'opt' matches, ie. which one
        it jest an unambiguous abbreviation for.  Raises BadOptionError if
        'opt' doesn't unambiguously match any long option string.
        """
        zwróć _match_abbrev(opt, self._long_opt)

    def _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        jeżeli "=" w arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = Prawda
        inaczej:
            opt = arg
            had_explicit_value = Nieprawda

        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        jeżeli option.takes_value():
            nargs = option.nargs
            jeżeli len(rargs) < nargs:
                self.error(ngettext(
                    "%(option)s option requires %(number)d argument",
                    "%(option)s option requires %(number)d arguments",
                    nargs) % {"option": opt, "number": nargs})
            albo_inaczej nargs == 1:
                value = rargs.pop(0)
            inaczej:
                value = tuple(rargs[0:nargs])
                usuń rargs[0:nargs]

        albo_inaczej had_explicit_value:
            self.error(_("%s option does nie take a value") % opt)

        inaczej:
            value = Nic

        option.process(opt, value, values, self)

    def _process_short_opts(self, rargs, values):
        arg = rargs.pop(0)
        stop = Nieprawda
        i = 1
        dla ch w arg[1:]:
            opt = "-" + ch
            option = self._short_opt.get(opt)
            i += 1                      # we have consumed a character

            jeżeli nie option:
                podnieś BadOptionError(opt)
            jeżeli option.takes_value():
                # Any characters left w arg?  Pretend they're the
                # next arg, oraz stop consuming characters of arg.
                jeżeli i < len(arg):
                    rargs.insert(0, arg[i:])
                    stop = Prawda

                nargs = option.nargs
                jeżeli len(rargs) < nargs:
                    self.error(ngettext(
                        "%(option)s option requires %(number)d argument",
                        "%(option)s option requires %(number)d arguments",
                        nargs) % {"option": opt, "number": nargs})
                albo_inaczej nargs == 1:
                    value = rargs.pop(0)
                inaczej:
                    value = tuple(rargs[0:nargs])
                    usuń rargs[0:nargs]

            inaczej:                       # option doesn't take a value
                value = Nic

            option.process(opt, value, values, self)

            jeżeli stop:
                przerwij


    # -- Feedback methods ----------------------------------------------

    def get_prog_name(self):
        jeżeli self.prog jest Nic:
            zwróć os.path.basename(sys.argv[0])
        inaczej:
            zwróć self.prog

    def expand_prog_name(self, s):
        zwróć s.replace("%prog", self.get_prog_name())

    def get_description(self):
        zwróć self.expand_prog_name(self.description)

    def exit(self, status=0, msg=Nic):
        jeżeli msg:
            sys.stderr.write(msg)
        sys.exit(status)

    def error(self, msg):
        """error(msg : string)

        Print a usage message incorporating 'msg' to stderr oraz exit.
        If you override this w a subclass, it should nie zwróć -- it
        should either exit albo podnieś an exception.
        """
        self.print_usage(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))

    def get_usage(self):
        jeżeli self.usage:
            zwróć self.formatter.format_usage(
                self.expand_prog_name(self.usage))
        inaczej:
            zwróć ""

    def print_usage(self, file=Nic):
        """print_usage(file : file = stdout)

        Print the usage message dla the current program (self.usage) to
        'file' (default stdout).  Any occurrence of the string "%prog" w
        self.usage jest replaced przy the name of the current program
        (basename of sys.argv[0]).  Does nothing jeżeli self.usage jest empty
        albo nie defined.
        """
        jeżeli self.usage:
            print(self.get_usage(), file=file)

    def get_version(self):
        jeżeli self.version:
            zwróć self.expand_prog_name(self.version)
        inaczej:
            zwróć ""

    def print_version(self, file=Nic):
        """print_version(file : file = stdout)

        Print the version message dla this program (self.version) to
        'file' (default stdout).  As przy print_usage(), any occurrence
        of "%prog" w self.version jest replaced by the current program's
        name.  Does nothing jeżeli self.version jest empty albo undefined.
        """
        jeżeli self.version:
            print(self.get_version(), file=file)

    def format_option_help(self, formatter=Nic):
        jeżeli formatter jest Nic:
            formatter = self.formatter
        formatter.store_option_strings(self)
        result = []
        result.append(formatter.format_heading(_("Options")))
        formatter.indent()
        jeżeli self.option_list:
            result.append(OptionContainer.format_option_help(self, formatter))
            result.append("\n")
        dla group w self.option_groups:
            result.append(group.format_help(formatter))
            result.append("\n")
        formatter.dedent()
        # Drop the last "\n", albo the header jeżeli no options albo option groups:
        zwróć "".join(result[:-1])

    def format_epilog(self, formatter):
        zwróć formatter.format_epilog(self.epilog)

    def format_help(self, formatter=Nic):
        jeżeli formatter jest Nic:
            formatter = self.formatter
        result = []
        jeżeli self.usage:
            result.append(self.get_usage() + "\n")
        jeżeli self.description:
            result.append(self.format_description(formatter) + "\n")
        result.append(self.format_option_help(formatter))
        result.append(self.format_epilog(formatter))
        zwróć "".join(result)

    def print_help(self, file=Nic):
        """print_help(file : file = stdout)

        Print an extended help message, listing all options oraz any
        help text provided przy them, to 'file' (default stdout).
        """
        jeżeli file jest Nic:
            file = sys.stdout
        file.write(self.format_help())

# klasa OptionParser


def _match_abbrev(s, wordmap):
    """_match_abbrev(s : string, wordmap : {string : Option}) -> string

    Return the string key w 'wordmap' dla which 's' jest an unambiguous
    abbreviation.  If 's' jest found to be ambiguous albo doesn't match any of
    'words', podnieś BadOptionError.
    """
    # Is there an exact match?
    jeżeli s w wordmap:
        zwróć s
    inaczej:
        # Isolate all words przy s jako a prefix.
        possibilities = [word dla word w wordmap.keys()
                         jeżeli word.startswith(s)]
        # No exact match, so there had better be just one possibility.
        jeżeli len(possibilities) == 1:
            zwróć possibilities[0]
        albo_inaczej nie possibilities:
            podnieś BadOptionError(s)
        inaczej:
            # More than one possible completion: ambiguous prefix.
            possibilities.sort()
            podnieś AmbiguousOptionError(s, possibilities)


# Some day, there might be many Option classes.  As of Optik 1.3, the
# preferred way to instantiate Options jest indirectly, via make_option(),
# which will become a factory function when there are many Option
# classes.
make_option = Option
