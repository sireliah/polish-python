# Author: Steven J. Bethard <steven.bethard@gmail.com>.

"""Command-line parsing library

This module jest an optparse-inspired command-line parsing library that:

    - handles both optional oraz positional arguments
    - produces highly informative usage messages
    - supports parsers that dispatch to sub-parsers

The following jest a simple usage example that sums integers z the
command-line oraz writes the result to a file::

    parser = argparse.ArgumentParser(
        description='sum the integers at the command line')
    parser.add_argument(
        'integers', metavar='int', nargs='+', type=int,
        help='an integer to be summed')
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the sum should be written')
    args = parser.parse_args()
    args.log.write('%s' % sum(args.integers))
    args.log.close()

The module contains the following public classes:

    - ArgumentParser -- The main entry point dla command-line parsing. As the
        example above shows, the add_argument() method jest used to populate
        the parser przy actions dla optional oraz positional arguments. Then
        the parse_args() method jest invoked to convert the args at the
        command-line into an object przy attributes.

    - ArgumentError -- The exception podnieśd by ArgumentParser objects when
        there are errors przy the parser's actions. Errors podnieśd while
        parsing the command-line are caught by ArgumentParser oraz emitted
        jako command-line messages.

    - FileType -- A factory dla defining types of files to be created. As the
        example above shows, instances of FileType are typically dalejed as
        the type= argument of add_argument() calls.

    - Action -- The base klasa dla parser actions. Typically actions are
        selected by dalejing strings like 'store_true' albo 'append_const' to
        the action= argument of add_argument(). However, dla greater
        customization of ArgumentParser actions, subclasses of Action may
        be defined oraz dalejed jako the action= argument.

    - HelpFormatter, RawDescriptionHelpFormatter, RawTextHelpFormatter,
        ArgumentDefaultsHelpFormatter -- Formatter classes which
        may be dalejed jako the formatter_class= argument to the
        ArgumentParser constructor. HelpFormatter jest the default,
        RawDescriptionHelpFormatter oraz RawTextHelpFormatter tell the parser
        nie to change the formatting dla help text, oraz
        ArgumentDefaultsHelpFormatter adds information about argument defaults
        to the help.

All other classes w this module are considered implementation details.
(Also note that HelpFormatter oraz RawDescriptionHelpFormatter are only
considered public jako object names -- the API of the formatter objects jest
still considered an implementation detail.)
"""

__version__ = '1.1'
__all__ = [
    'ArgumentParser',
    'ArgumentError',
    'ArgumentTypeError',
    'FileType',
    'HelpFormatter',
    'ArgumentDefaultsHelpFormatter',
    'RawDescriptionHelpFormatter',
    'RawTextHelpFormatter',
    'MetavarTypeHelpFormatter',
    'Namespace',
    'Action',
    'ONE_OR_MORE',
    'OPTIONAL',
    'PARSER',
    'REMAINDER',
    'SUPPRESS',
    'ZERO_OR_MORE',
]


zaimportuj collections jako _collections
zaimportuj copy jako _copy
zaimportuj os jako _os
zaimportuj re jako _re
zaimportuj sys jako _sys
zaimportuj textwrap jako _textwrap

z gettext zaimportuj gettext jako _, ngettext


SUPPRESS = '==SUPPRESS=='

OPTIONAL = '?'
ZERO_OR_MORE = '*'
ONE_OR_MORE = '+'
PARSER = 'A...'
REMAINDER = '...'
_UNRECOGNIZED_ARGS_ATTR = '_unrecognized_args'

# =============================
# Utility functions oraz classes
# =============================

klasa _AttributeHolder(object):
    """Abstract base klasa that provides __repr__.

    The __repr__ method returns a string w the format::
        ClassName(attr=name, attr=name, ...)
    The attributes are determined either by a class-level attribute,
    '_kwarg_names', albo by inspecting the instance __dict__.
    """

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        dla arg w self._get_args():
            arg_strings.append(repr(arg))
        dla name, value w self._get_kwargs():
            arg_strings.append('%s=%r' % (name, value))
        zwróć '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        zwróć sorted(self.__dict__.items())

    def _get_args(self):
        zwróć []


def _ensure_value(namespace, name, value):
    jeżeli getattr(namespace, name, Nic) jest Nic:
        setattr(namespace, name, value)
    zwróć getattr(namespace, name)


# ===============
# Formatting Help
# ===============

klasa HelpFormatter(object):
    """Formatter dla generating usage messages oraz argument help strings.

    Only the name of this klasa jest considered a public API. All the methods
    provided by the klasa are considered an implementation detail.
    """

    def __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=24,
                 width=Nic):

        # default setting dla width
        jeżeli width jest Nic:
            spróbuj:
                width = int(_os.environ['COLUMNS'])
            wyjąwszy (KeyError, ValueError):
                width = 80
            width -= 2

        self._prog = prog
        self._indent_increment = indent_increment
        self._max_help_position = max_help_position
        self._max_help_position = min(max_help_position,
                                      max(width - 20, indent_increment * 2))
        self._width = width

        self._current_indent = 0
        self._level = 0
        self._action_max_length = 0

        self._root_section = self._Section(self, Nic)
        self._current_section = self._root_section

        self._whitespace_matcher = _re.compile(r'\s+')
        self._long_break_matcher = _re.compile(r'\n\n\n+')

    # ===============================
    # Section oraz indentation methods
    # ===============================
    def _indent(self):
        self._current_indent += self._indent_increment
        self._level += 1

    def _dedent(self):
        self._current_indent -= self._indent_increment
        assert self._current_indent >= 0, 'Indent decreased below 0.'
        self._level -= 1

    klasa _Section(object):

        def __init__(self, formatter, parent, heading=Nic):
            self.formatter = formatter
            self.parent = parent
            self.heading = heading
            self.items = []

        def format_help(self):
            # format the indented section
            jeżeli self.parent jest nie Nic:
                self.formatter._indent()
            join = self.formatter._join_parts
            dla func, args w self.items:
                func(*args)
            item_help = join([func(*args) dla func, args w self.items])
            jeżeli self.parent jest nie Nic:
                self.formatter._dedent()

            # zwróć nothing jeżeli the section was empty
            jeżeli nie item_help:
                zwróć ''

            # add the heading jeżeli the section was non-empty
            jeżeli self.heading jest nie SUPPRESS oraz self.heading jest nie Nic:
                current_indent = self.formatter._current_indent
                heading = '%*s%s:\n' % (current_indent, '', self.heading)
            inaczej:
                heading = ''

            # join the section-initial newline, the heading oraz the help
            zwróć join(['\n', heading, item_help, '\n'])

    def _add_item(self, func, args):
        self._current_section.items.append((func, args))

    # ========================
    # Message building methods
    # ========================
    def start_section(self, heading):
        self._indent()
        section = self._Section(self, self._current_section, heading)
        self._add_item(section.format_help, [])
        self._current_section = section

    def end_section(self):
        self._current_section = self._current_section.parent
        self._dedent()

    def add_text(self, text):
        jeżeli text jest nie SUPPRESS oraz text jest nie Nic:
            self._add_item(self._format_text, [text])

    def add_usage(self, usage, actions, groups, prefix=Nic):
        jeżeli usage jest nie SUPPRESS:
            args = usage, actions, groups, prefix
            self._add_item(self._format_usage, args)

    def add_argument(self, action):
        jeżeli action.help jest nie SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            dla subaction w self._iter_indented_subactions(action):
                invocations.append(get_invocation(subaction))

            # update the maximum item length
            invocation_length = max([len(s) dla s w invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    def add_arguments(self, actions):
        dla action w actions:
            self.add_argument(action)

    # =======================
    # Help-formatting methods
    # =======================
    def format_help(self):
        help = self._root_section.format_help()
        jeżeli help:
            help = self._long_break_matcher.sub('\n\n', help)
            help = help.strip('\n') + '\n'
        zwróć help

    def _join_parts(self, part_strings):
        zwróć ''.join([part
                        dla part w part_strings
                        jeżeli part oraz part jest nie SUPPRESS])

    def _format_usage(self, usage, actions, groups, prefix):
        jeżeli prefix jest Nic:
            prefix = _('usage: ')

        # jeżeli usage jest specified, use that
        jeżeli usage jest nie Nic:
            usage = usage % dict(prog=self._prog)

        # jeżeli no optionals albo positionals are available, usage jest just prog
        albo_inaczej usage jest Nic oraz nie actions:
            usage = '%(prog)s' % dict(prog=self._prog)

        # jeżeli optionals oraz positionals are available, calculate usage
        albo_inaczej usage jest Nic:
            prog = '%(prog)s' % dict(prog=self._prog)

            # split optionals z positionals
            optionals = []
            positionals = []
            dla action w actions:
                jeżeli action.option_strings:
                    optionals.append(action)
                inaczej:
                    positionals.append(action)

            # build full usage string
            format = self._format_actions_usage
            action_usage = format(optionals + positionals, groups)
            usage = ' '.join([s dla s w [prog, action_usage] jeżeli s])

            # wrap the usage parts jeżeli it's too long
            text_width = self._width - self._current_indent
            jeżeli len(prefix) + len(usage) > text_width:

                # przerwij usage into wrappable parts
                part_regexp = r'\(.*?\)+|\[.*?\]+|\S+'
                opt_usage = format(optionals, groups)
                pos_usage = format(positionals, groups)
                opt_parts = _re.findall(part_regexp, opt_usage)
                pos_parts = _re.findall(part_regexp, pos_usage)
                assert ' '.join(opt_parts) == opt_usage
                assert ' '.join(pos_parts) == pos_usage

                # helper dla wrapping lines
                def get_lines(parts, indent, prefix=Nic):
                    lines = []
                    line = []
                    jeżeli prefix jest nie Nic:
                        line_len = len(prefix) - 1
                    inaczej:
                        line_len = len(indent) - 1
                    dla part w parts:
                        jeżeli line_len + 1 + len(part) > text_width oraz line:
                            lines.append(indent + ' '.join(line))
                            line = []
                            line_len = len(indent) - 1
                        line.append(part)
                        line_len += len(part) + 1
                    jeżeli line:
                        lines.append(indent + ' '.join(line))
                    jeżeli prefix jest nie Nic:
                        lines[0] = lines[0][len(indent):]
                    zwróć lines

                # jeżeli prog jest short, follow it przy optionals albo positionals
                jeżeli len(prefix) + len(prog) <= 0.75 * text_width:
                    indent = ' ' * (len(prefix) + len(prog) + 1)
                    jeżeli opt_parts:
                        lines = get_lines([prog] + opt_parts, indent, prefix)
                        lines.extend(get_lines(pos_parts, indent))
                    albo_inaczej pos_parts:
                        lines = get_lines([prog] + pos_parts, indent, prefix)
                    inaczej:
                        lines = [prog]

                # jeżeli prog jest long, put it on its own line
                inaczej:
                    indent = ' ' * len(prefix)
                    parts = opt_parts + pos_parts
                    lines = get_lines(parts, indent)
                    jeżeli len(lines) > 1:
                        lines = []
                        lines.extend(get_lines(opt_parts, indent))
                        lines.extend(get_lines(pos_parts, indent))
                    lines = [prog] + lines

                # join lines into usage
                usage = '\n'.join(lines)

        # prefix przy 'usage:'
        zwróć '%s%s\n\n' % (prefix, usage)

    def _format_actions_usage(self, actions, groups):
        # find group indices oraz identify actions w groups
        group_actions = set()
        inserts = {}
        dla group w groups:
            spróbuj:
                start = actions.index(group._group_actions[0])
            wyjąwszy ValueError:
                kontynuuj
            inaczej:
                end = start + len(group._group_actions)
                jeżeli actions[start:end] == group._group_actions:
                    dla action w group._group_actions:
                        group_actions.add(action)
                    jeżeli nie group.required:
                        jeżeli start w inserts:
                            inserts[start] += ' ['
                        inaczej:
                            inserts[start] = '['
                        inserts[end] = ']'
                    inaczej:
                        jeżeli start w inserts:
                            inserts[start] += ' ('
                        inaczej:
                            inserts[start] = '('
                        inserts[end] = ')'
                    dla i w range(start + 1, end):
                        inserts[i] = '|'

        # collect all actions format strings
        parts = []
        dla i, action w enumerate(actions):

            # suppressed arguments are marked przy Nic
            # remove | separators dla suppressed arguments
            jeżeli action.help jest SUPPRESS:
                parts.append(Nic)
                jeżeli inserts.get(i) == '|':
                    inserts.pop(i)
                albo_inaczej inserts.get(i + 1) == '|':
                    inserts.pop(i + 1)

            # produce all arg strings
            albo_inaczej nie action.option_strings:
                default = self._get_default_metavar_for_positional(action)
                part = self._format_args(action, default)

                # jeżeli it's w a group, strip the outer []
                jeżeli action w group_actions:
                    jeżeli part[0] == '[' oraz part[-1] == ']':
                        part = part[1:-1]

                # add the action string to the list
                parts.append(part)

            # produce the first way to invoke the option w brackets
            inaczej:
                option_string = action.option_strings[0]

                # jeżeli the Optional doesn't take a value, format is:
                #    -s albo --long
                jeżeli action.nargs == 0:
                    part = '%s' % option_string

                # jeżeli the Optional takes a value, format is:
                #    -s ARGS albo --long ARGS
                inaczej:
                    default = self._get_default_metavar_for_optional(action)
                    args_string = self._format_args(action, default)
                    part = '%s %s' % (option_string, args_string)

                # make it look optional jeżeli it's nie required albo w a group
                jeżeli nie action.required oraz action nie w group_actions:
                    part = '[%s]' % part

                # add the action string to the list
                parts.append(part)

        # insert things at the necessary indices
        dla i w sorted(inserts, reverse=Prawda):
            parts[i:i] = [inserts[i]]

        # join all the action items przy spaces
        text = ' '.join([item dla item w parts jeżeli item jest nie Nic])

        # clean up separators dla mutually exclusive groups
        open = r'[\[(]'
        close = r'[\])]'
        text = _re.sub(r'(%s) ' % open, r'\1', text)
        text = _re.sub(r' (%s)' % close, r'\1', text)
        text = _re.sub(r'%s *%s' % (open, close), r'', text)
        text = _re.sub(r'\(([^|]*)\)', r'\1', text)
        text = text.strip()

        # zwróć the text
        zwróć text

    def _format_text(self, text):
        jeżeli '%(prog)' w text:
            text = text % dict(prog=self._prog)
        text_width = max(self._width - self._current_indent, 11)
        indent = ' ' * self._current_indent
        zwróć self._fill_text(text, text_width, indent) + '\n\n'

    def _format_action(self, action):
        # determine the required width oraz the entry label
        help_position = min(self._action_max_length + 2,
                            self._max_help_position)
        help_width = max(self._width - help_position, 11)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)

        # no help; start on same line oraz add a final newline
        jeżeli nie action.help:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup

        # short action name; start on the same line oraz pad two spaces
        albo_inaczej len(action_header) <= action_width:
            tup = self._current_indent, '', action_width, action_header
            action_header = '%*s%-*s  ' % tup
            indent_first = 0

        # long action name; start on the next line
        inaczej:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup
            indent_first = help_position

        # collect the pieces of the action help
        parts = [action_header]

        # jeżeli there was help dla the action, add lines of help text
        jeżeli action.help:
            help_text = self._expand_help(action)
            help_lines = self._split_lines(help_text, help_width)
            parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
            dla line w help_lines[1:]:
                parts.append('%*s%s\n' % (help_position, '', line))

        # albo add a newline jeżeli the description doesn't end przy one
        albo_inaczej nie action_header.endswith('\n'):
            parts.append('\n')

        # jeżeli there are any sub-actions, add their help jako well
        dla subaction w self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        # zwróć a single string
        zwróć self._join_parts(parts)

    def _format_action_invocation(self, action):
        jeżeli nie action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            zwróć metavar

        inaczej:
            parts = []

            # jeżeli the Optional doesn't take a value, format is:
            #    -s, --long
            jeżeli action.nargs == 0:
                parts.extend(action.option_strings)

            # jeżeli the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            inaczej:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                dla option_string w action.option_strings:
                    parts.append('%s %s' % (option_string, args_string))

            zwróć ', '.join(parts)

    def _metavar_formatter(self, action, default_metavar):
        jeżeli action.metavar jest nie Nic:
            result = action.metavar
        albo_inaczej action.choices jest nie Nic:
            choice_strs = [str(choice) dla choice w action.choices]
            result = '{%s}' % ','.join(choice_strs)
        inaczej:
            result = default_metavar

        def format(tuple_size):
            jeżeli isinstance(result, tuple):
                zwróć result
            inaczej:
                zwróć (result, ) * tuple_size
        zwróć format

    def _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        jeżeli action.nargs jest Nic:
            result = '%s' % get_metavar(1)
        albo_inaczej action.nargs == OPTIONAL:
            result = '[%s]' % get_metavar(1)
        albo_inaczej action.nargs == ZERO_OR_MORE:
            result = '[%s [%s ...]]' % get_metavar(2)
        albo_inaczej action.nargs == ONE_OR_MORE:
            result = '%s [%s ...]' % get_metavar(2)
        albo_inaczej action.nargs == REMAINDER:
            result = '...'
        albo_inaczej action.nargs == PARSER:
            result = '%s ...' % get_metavar(1)
        inaczej:
            formats = ['%s' dla _ w range(action.nargs)]
            result = ' '.join(formats) % get_metavar(action.nargs)
        zwróć result

    def _expand_help(self, action):
        params = dict(vars(action), prog=self._prog)
        dla name w list(params):
            jeżeli params[name] jest SUPPRESS:
                usuń params[name]
        dla name w list(params):
            jeżeli hasattr(params[name], '__name__'):
                params[name] = params[name].__name__
        jeżeli params.get('choices') jest nie Nic:
            choices_str = ', '.join([str(c) dla c w params['choices']])
            params['choices'] = choices_str
        zwróć self._get_help_string(action) % params

    def _iter_indented_subactions(self, action):
        spróbuj:
            get_subactions = action._get_subactions
        wyjąwszy AttributeError:
            dalej
        inaczej:
            self._indent()
            uzyskaj z get_subactions()
            self._dedent()

    def _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        zwróć _textwrap.wrap(text, width)

    def _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        zwróć _textwrap.fill(text, width, initial_indent=indent,
                                           subsequent_indent=indent)

    def _get_help_string(self, action):
        zwróć action.help

    def _get_default_metavar_for_optional(self, action):
        zwróć action.dest.upper()

    def _get_default_metavar_for_positional(self, action):
        zwróć action.dest


klasa RawDescriptionHelpFormatter(HelpFormatter):
    """Help message formatter which retains any formatting w descriptions.

    Only the name of this klasa jest considered a public API. All the methods
    provided by the klasa are considered an implementation detail.
    """

    def _fill_text(self, text, width, indent):
        zwróć ''.join(indent + line dla line w text.splitlines(keepends=Prawda))


klasa RawTextHelpFormatter(RawDescriptionHelpFormatter):
    """Help message formatter which retains formatting of all help text.

    Only the name of this klasa jest considered a public API. All the methods
    provided by the klasa are considered an implementation detail.
    """

    def _split_lines(self, text, width):
        zwróć text.splitlines()


klasa ArgumentDefaultsHelpFormatter(HelpFormatter):
    """Help message formatter which adds default values to argument help.

    Only the name of this klasa jest considered a public API. All the methods
    provided by the klasa are considered an implementation detail.
    """

    def _get_help_string(self, action):
        help = action.help
        jeżeli '%(default)' nie w action.help:
            jeżeli action.default jest nie SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                jeżeli action.option_strings albo action.nargs w defaulting_nargs:
                    help += ' (default: %(default)s)'
        zwróć help


klasa MetavarTypeHelpFormatter(HelpFormatter):
    """Help message formatter which uses the argument 'type' jako the default
    metavar value (instead of the argument 'dest')

    Only the name of this klasa jest considered a public API. All the methods
    provided by the klasa are considered an implementation detail.
    """

    def _get_default_metavar_for_optional(self, action):
        zwróć action.type.__name__

    def _get_default_metavar_for_positional(self, action):
        zwróć action.type.__name__



# =====================
# Options oraz Arguments
# =====================

def _get_action_name(argument):
    jeżeli argument jest Nic:
        zwróć Nic
    albo_inaczej argument.option_strings:
        zwróć  '/'.join(argument.option_strings)
    albo_inaczej argument.metavar nie w (Nic, SUPPRESS):
        zwróć argument.metavar
    albo_inaczej argument.dest nie w (Nic, SUPPRESS):
        zwróć argument.dest
    inaczej:
        zwróć Nic


klasa ArgumentError(Exception):
    """An error z creating albo using an argument (optional albo positional).

    The string value of this exception jest the message, augmented with
    information about the argument that caused it.
    """

    def __init__(self, argument, message):
        self.argument_name = _get_action_name(argument)
        self.message = message

    def __str__(self):
        jeżeli self.argument_name jest Nic:
            format = '%(message)s'
        inaczej:
            format = 'argument %(argument_name)s: %(message)s'
        zwróć format % dict(message=self.message,
                             argument_name=self.argument_name)


klasa ArgumentTypeError(Exception):
    """An error z trying to convert a command line string to a type."""
    dalej


# ==============
# Action classes
# ==============

klasa Action(_AttributeHolder):
    """Information about how to convert command line strings to Python objects.

    Action objects are used by an ArgumentParser to represent the information
    needed to parse a single argument z one albo more strings z the
    command line. The keyword arguments to the Action constructor are also
    all attributes of Action instances.

    Keyword Arguments:

        - option_strings -- A list of command-line option strings which
            should be associated przy this action.

        - dest -- The name of the attribute to hold the created object(s)

        - nargs -- The number of command-line arguments that should be
            consumed. By default, one argument will be consumed oraz a single
            value will be produced.  Other values include:
                - N (an integer) consumes N arguments (and produces a list)
                - '?' consumes zero albo one arguments
                - '*' consumes zero albo more arguments (and produces a list)
                - '+' consumes one albo more arguments (and produces a list)
            Note that the difference between the default oraz nargs=1 jest that
            przy the default, a single value will be produced, dopóki with
            nargs=1, a list containing a single value will be produced.

        - const -- The value to be produced jeżeli the option jest specified oraz the
            option uses an action that takes no values.

        - default -- The value to be produced jeżeli the option jest nie specified.

        - type -- A callable that accepts a single string argument, oraz
            returns the converted value.  The standard Python types str, int,
            float, oraz complex are useful examples of such callables.  If Nic,
            str jest used.

        - choices -- A container of values that should be allowed. If nie Nic,
            after a command-line argument has been converted to the appropriate
            type, an exception will be podnieśd jeżeli it jest nie a member of this
            collection.

        - required -- Prawda jeżeli the action must always be specified at the
            command line. This jest only meaningful dla optional command-line
            arguments.

        - help -- The help string describing the argument.

        - metavar -- The name to be used dla the option's argument przy the
            help string. If Nic, the 'dest' value will be used jako the name.
    """

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=Nic,
                 const=Nic,
                 default=Nic,
                 type=Nic,
                 choices=Nic,
                 required=Nieprawda,
                 help=Nic,
                 metavar=Nic):
        self.option_strings = option_strings
        self.dest = dest
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.choices = choices
        self.required = required
        self.help = help
        self.metavar = metavar

    def _get_kwargs(self):
        names = [
            'option_strings',
            'dest',
            'nargs',
            'const',
            'default',
            'type',
            'choices',
            'help',
            'metavar',
        ]
        zwróć [(name, getattr(self, name)) dla name w names]

    def __call__(self, parser, namespace, values, option_string=Nic):
        podnieś NotImplementedError(_('.__call__() nie defined'))


klasa _StoreAction(Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=Nic,
                 const=Nic,
                 default=Nic,
                 type=Nic,
                 choices=Nic,
                 required=Nieprawda,
                 help=Nic,
                 metavar=Nic):
        jeżeli nargs == 0:
            podnieś ValueError('nargs dla store actions must be > 0; jeżeli you '
                             'have nothing to store, actions such jako store '
                             'true albo store const may be more appropriate')
        jeżeli const jest nie Nic oraz nargs != OPTIONAL:
            podnieś ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(_StoreAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=Nic):
        setattr(namespace, self.dest, values)


klasa _StoreConstAction(Action):

    def __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=Nic,
                 required=Nieprawda,
                 help=Nic,
                 metavar=Nic):
        super(_StoreConstAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=const,
            default=default,
            required=required,
            help=help)

    def __call__(self, parser, namespace, values, option_string=Nic):
        setattr(namespace, self.dest, self.const)


klasa _StorePrawdaAction(_StoreConstAction):

    def __init__(self,
                 option_strings,
                 dest,
                 default=Nieprawda,
                 required=Nieprawda,
                 help=Nic):
        super(_StorePrawdaAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            const=Prawda,
            default=default,
            required=required,
            help=help)


klasa _StoreNieprawdaAction(_StoreConstAction):

    def __init__(self,
                 option_strings,
                 dest,
                 default=Prawda,
                 required=Nieprawda,
                 help=Nic):
        super(_StoreNieprawdaAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            const=Nieprawda,
            default=default,
            required=required,
            help=help)


klasa _AppendAction(Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=Nic,
                 const=Nic,
                 default=Nic,
                 type=Nic,
                 choices=Nic,
                 required=Nieprawda,
                 help=Nic,
                 metavar=Nic):
        jeżeli nargs == 0:
            podnieś ValueError('nargs dla append actions must be > 0; jeżeli arg '
                             'strings are nie supplying the value to append, '
                             'the append const action may be more appropriate')
        jeżeli const jest nie Nic oraz nargs != OPTIONAL:
            podnieś ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(_AppendAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=Nic):
        items = _copy.copy(_ensure_value(namespace, self.dest, []))
        items.append(values)
        setattr(namespace, self.dest, items)


klasa _AppendConstAction(Action):

    def __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=Nic,
                 required=Nieprawda,
                 help=Nic,
                 metavar=Nic):
        super(_AppendConstAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=const,
            default=default,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=Nic):
        items = _copy.copy(_ensure_value(namespace, self.dest, []))
        items.append(self.const)
        setattr(namespace, self.dest, items)


klasa _CountAction(Action):

    def __init__(self,
                 option_strings,
                 dest,
                 default=Nic,
                 required=Nieprawda,
                 help=Nic):
        super(_CountAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            required=required,
            help=help)

    def __call__(self, parser, namespace, values, option_string=Nic):
        new_count = _ensure_value(namespace, self.dest, 0) + 1
        setattr(namespace, self.dest, new_count)


klasa _HelpAction(Action):

    def __init__(self,
                 option_strings,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help=Nic):
        super(_HelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=Nic):
        parser.print_help()
        parser.exit()


klasa _VersionAction(Action):

    def __init__(self,
                 option_strings,
                 version=Nic,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help="show program's version number oraz exit"):
        super(_VersionAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=Nic):
        version = self.version
        jeżeli version jest Nic:
            version = parser.version
        formatter = parser._get_formatter()
        formatter.add_text(version)
        parser._print_message(formatter.format_help(), _sys.stdout)
        parser.exit()


klasa _SubParsersAction(Action):

    klasa _ChoicesPseudoAction(Action):

        def __init__(self, name, aliases, help):
            metavar = dest = name
            jeżeli aliases:
                metavar += ' (%s)' % ', '.join(aliases)
            sup = super(_SubParsersAction._ChoicesPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help,
                         metavar=metavar)

    def __init__(self,
                 option_strings,
                 prog,
                 parser_class,
                 dest=SUPPRESS,
                 help=Nic,
                 metavar=Nic):

        self._prog_prefix = prog
        self._parser_class = parser_class
        self._name_parser_map = _collections.OrderedDict()
        self._choices_actions = []

        super(_SubParsersAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=PARSER,
            choices=self._name_parser_map,
            help=help,
            metavar=metavar)

    def add_parser(self, name, **kwargs):
        # set prog z the existing prefix
        jeżeli kwargs.get('prog') jest Nic:
            kwargs['prog'] = '%s %s' % (self._prog_prefix, name)

        aliases = kwargs.pop('aliases', ())

        # create a pseudo-action to hold the choice help
        jeżeli 'help' w kwargs:
            help = kwargs.pop('help')
            choice_action = self._ChoicesPseudoAction(name, aliases, help)
            self._choices_actions.append(choice_action)

        # create the parser oraz add it to the map
        parser = self._parser_class(**kwargs)
        self._name_parser_map[name] = parser

        # make parser available under aliases also
        dla alias w aliases:
            self._name_parser_map[alias] = parser

        zwróć parser

    def _get_subactions(self):
        zwróć self._choices_actions

    def __call__(self, parser, namespace, values, option_string=Nic):
        parser_name = values[0]
        arg_strings = values[1:]

        # set the parser name jeżeli requested
        jeżeli self.dest jest nie SUPPRESS:
            setattr(namespace, self.dest, parser_name)

        # select the parser
        spróbuj:
            parser = self._name_parser_map[parser_name]
        wyjąwszy KeyError:
            args = {'parser_name': parser_name,
                    'choices': ', '.join(self._name_parser_map)}
            msg = _('unknown parser %(parser_name)r (choices: %(choices)s)') % args
            podnieś ArgumentError(self, msg)

        # parse all the remaining options into the namespace
        # store any unrecognized options on the object, so that the top
        # level parser can decide what to do przy them

        # In case this subparser defines new defaults, we parse them
        # w a new namespace object oraz then update the original
        # namespace dla the relevant parts.
        subnamespace, arg_strings = parser.parse_known_args(arg_strings, Nic)
        dla key, value w vars(subnamespace).items():
            setattr(namespace, key, value)

        jeżeli arg_strings:
            vars(namespace).setdefault(_UNRECOGNIZED_ARGS_ATTR, [])
            getattr(namespace, _UNRECOGNIZED_ARGS_ATTR).extend(arg_strings)


# ==============
# Type classes
# ==============

klasa FileType(object):
    """Factory dla creating file object types

    Instances of FileType are typically dalejed jako type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - mode -- A string indicating how the file jest to be opened. Accepts the
            same values jako the builtin open() function.
        - bufsize -- The file's desired buffer size. Accepts the same values as
            the builtin open() function.
        - encoding -- The file's encoding. Accepts the same values jako the
            builtin open() function.
        - errors -- A string indicating how encoding oraz decoding errors are to
            be handled. Accepts the same value jako the builtin open() function.
    """

    def __init__(self, mode='r', bufsize=-1, encoding=Nic, errors=Nic):
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

    def __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        jeżeli string == '-':
            jeżeli 'r' w self._mode:
                zwróć _sys.stdin
            albo_inaczej 'w' w self._mode:
                zwróć _sys.stdout
            inaczej:
                msg = _('argument "-" przy mode %r') % self._mode
                podnieś ValueError(msg)

        # all other arguments are used jako file names
        spróbuj:
            zwróć open(string, self._mode, self._bufsize, self._encoding,
                        self._errors)
        wyjąwszy OSError jako e:
            message = _("can't open '%s': %s")
            podnieś ArgumentTypeError(message % (string, e))

    def __repr__(self):
        args = self._mode, self._bufsize
        kwargs = [('encoding', self._encoding), ('errors', self._errors)]
        args_str = ', '.join([repr(arg) dla arg w args jeżeli arg != -1] +
                             ['%s=%r' % (kw, arg) dla kw, arg w kwargs
                              jeżeli arg jest nie Nic])
        zwróć '%s(%s)' % (type(self).__name__, args_str)

# ===========================
# Optional oraz Positional Parsing
# ===========================

klasa Namespace(_AttributeHolder):
    """Simple object dla storing attributes.

    Implements equality by attribute names oraz values, oraz provides a simple
    string representation.
    """

    def __init__(self, **kwargs):
        dla name w kwargs:
            setattr(self, name, kwargs[name])

    def __eq__(self, other):
        jeżeli nie isinstance(other, Namespace):
            zwróć NotImplemented
        zwróć vars(self) == vars(other)

    def __contains__(self, key):
        zwróć key w self.__dict__


klasa _ActionsContainer(object):

    def __init__(self,
                 description,
                 prefix_chars,
                 argument_default,
                 conflict_handler):
        super(_ActionsContainer, self).__init__()

        self.description = description
        self.argument_default = argument_default
        self.prefix_chars = prefix_chars
        self.conflict_handler = conflict_handler

        # set up registries
        self._registries = {}

        # register actions
        self.register('action', Nic, _StoreAction)
        self.register('action', 'store', _StoreAction)
        self.register('action', 'store_const', _StoreConstAction)
        self.register('action', 'store_true', _StorePrawdaAction)
        self.register('action', 'store_false', _StoreNieprawdaAction)
        self.register('action', 'append', _AppendAction)
        self.register('action', 'append_const', _AppendConstAction)
        self.register('action', 'count', _CountAction)
        self.register('action', 'help', _HelpAction)
        self.register('action', 'version', _VersionAction)
        self.register('action', 'parsers', _SubParsersAction)

        # podnieś an exception jeżeli the conflict handler jest invalid
        self._get_handler()

        # action storage
        self._actions = []
        self._option_string_actions = {}

        # groups
        self._action_groups = []
        self._mutually_exclusive_groups = []

        # defaults storage
        self._defaults = {}

        # determines whether an "option" looks like a negative number
        self._negative_number_matcher = _re.compile(r'^-\d+$|^-\d*\.\d+$')

        # whether albo nie there are any optionals that look like negative
        # numbers -- uses a list so it can be shared oraz edited
        self._has_negative_number_optionals = []

    # ====================
    # Registration methods
    # ====================
    def register(self, registry_name, value, object):
        registry = self._registries.setdefault(registry_name, {})
        registry[value] = object

    def _registry_get(self, registry_name, value, default=Nic):
        zwróć self._registries[registry_name].get(value, default)

    # ==================================
    # Namespace default accessor methods
    # ==================================
    def set_defaults(self, **kwargs):
        self._defaults.update(kwargs)

        # jeżeli these defaults match any existing arguments, replace
        # the previous default on the object przy the new one
        dla action w self._actions:
            jeżeli action.dest w kwargs:
                action.default = kwargs[action.dest]

    def get_default(self, dest):
        dla action w self._actions:
            jeżeli action.dest == dest oraz action.default jest nie Nic:
                zwróć action.default
        zwróć self._defaults.get(dest, Nic)


    # =======================
    # Adding argument actions
    # =======================
    def add_argument(self, *args, **kwargs):
        """
        add_argument(dest, ..., name=value, ...)
        add_argument(option_string, option_string, ..., name=value, ...)
        """

        # jeżeli no positional args are supplied albo only one jest supplied oraz
        # it doesn't look like an option string, parse a positional
        # argument
        chars = self.prefix_chars
        jeżeli nie args albo len(args) == 1 oraz args[0][0] nie w chars:
            jeżeli args oraz 'dest' w kwargs:
                podnieś ValueError('dest supplied twice dla positional argument')
            kwargs = self._get_positional_kwargs(*args, **kwargs)

        # otherwise, we're adding an optional argument
        inaczej:
            kwargs = self._get_optional_kwargs(*args, **kwargs)

        # jeżeli no default was supplied, use the parser-level default
        jeżeli 'default' nie w kwargs:
            dest = kwargs['dest']
            jeżeli dest w self._defaults:
                kwargs['default'] = self._defaults[dest]
            albo_inaczej self.argument_default jest nie Nic:
                kwargs['default'] = self.argument_default

        # create the action object, oraz add it to the parser
        action_class = self._pop_action_class(kwargs)
        jeżeli nie callable(action_class):
            podnieś ValueError('unknown action "%s"' % (action_class,))
        action = action_class(**kwargs)

        # podnieś an error jeżeli the action type jest nie callable
        type_func = self._registry_get('type', action.type, action.type)
        jeżeli nie callable(type_func):
            podnieś ValueError('%r jest nie callable' % (type_func,))

        # podnieś an error jeżeli the metavar does nie match the type
        jeżeli hasattr(self, "_get_formatter"):
            spróbuj:
                self._get_formatter()._format_args(action, Nic)
            wyjąwszy TypeError:
                podnieś ValueError("length of metavar tuple does nie match nargs")

        zwróć self._add_action(action)

    def add_argument_group(self, *args, **kwargs):
        group = _ArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        zwróć group

    def add_mutually_exclusive_group(self, **kwargs):
        group = _MutuallyExclusiveGroup(self, **kwargs)
        self._mutually_exclusive_groups.append(group)
        zwróć group

    def _add_action(self, action):
        # resolve any conflicts
        self._check_conflict(action)

        # add to actions list
        self._actions.append(action)
        action.container = self

        # index the action by any option strings it has
        dla option_string w action.option_strings:
            self._option_string_actions[option_string] = action

        # set the flag jeżeli any option strings look like negative numbers
        dla option_string w action.option_strings:
            jeżeli self._negative_number_matcher.match(option_string):
                jeżeli nie self._has_negative_number_optionals:
                    self._has_negative_number_optionals.append(Prawda)

        # zwróć the created action
        zwróć action

    def _remove_action(self, action):
        self._actions.remove(action)

    def _add_container_actions(self, container):
        # collect groups by titles
        title_group_map = {}
        dla group w self._action_groups:
            jeżeli group.title w title_group_map:
                msg = _('cannot merge actions - two groups are named %r')
                podnieś ValueError(msg % (group.title))
            title_group_map[group.title] = group

        # map each action to its group
        group_map = {}
        dla group w container._action_groups:

            # jeżeli a group przy the title exists, use that, otherwise
            # create a new group matching the container's group
            jeżeli group.title nie w title_group_map:
                title_group_map[group.title] = self.add_argument_group(
                    title=group.title,
                    description=group.description,
                    conflict_handler=group.conflict_handler)

            # map the actions to their new group
            dla action w group._group_actions:
                group_map[action] = title_group_map[group.title]

        # add container's mutually exclusive groups
        # NOTE: jeżeli add_mutually_exclusive_group ever gains title= oraz
        # description= then this code will need to be expanded jako above
        dla group w container._mutually_exclusive_groups:
            mutex_group = self.add_mutually_exclusive_group(
                required=group.required)

            # map the actions to their new mutex group
            dla action w group._group_actions:
                group_map[action] = mutex_group

        # add all actions to this container albo their group
        dla action w container._actions:
            group_map.get(action, self)._add_action(action)

    def _get_positional_kwargs(self, dest, **kwargs):
        # make sure required jest nie specified
        jeżeli 'required' w kwargs:
            msg = _("'required' jest an invalid argument dla positionals")
            podnieś TypeError(msg)

        # mark positional arguments jako required jeżeli at least one jest
        # always required
        jeżeli kwargs.get('nargs') nie w [OPTIONAL, ZERO_OR_MORE]:
            kwargs['required'] = Prawda
        jeżeli kwargs.get('nargs') == ZERO_OR_MORE oraz 'default' nie w kwargs:
            kwargs['required'] = Prawda

        # zwróć the keyword arguments przy no option strings
        zwróć dict(kwargs, dest=dest, option_strings=[])

    def _get_optional_kwargs(self, *args, **kwargs):
        # determine short oraz long option strings
        option_strings = []
        long_option_strings = []
        dla option_string w args:
            # error on strings that don't start przy an appropriate prefix
            jeżeli nie option_string[0] w self.prefix_chars:
                args = {'option': option_string,
                        'prefix_chars': self.prefix_chars}
                msg = _('invalid option string %(option)r: '
                        'must start przy a character %(prefix_chars)r')
                podnieś ValueError(msg % args)

            # strings starting przy two prefix characters are long options
            option_strings.append(option_string)
            jeżeli option_string[0] w self.prefix_chars:
                jeżeli len(option_string) > 1:
                    jeżeli option_string[1] w self.prefix_chars:
                        long_option_strings.append(option_string)

        # infer destination, '--foo-bar' -> 'foo_bar' oraz '-x' -> 'x'
        dest = kwargs.pop('dest', Nic)
        jeżeli dest jest Nic:
            jeżeli long_option_strings:
                dest_option_string = long_option_strings[0]
            inaczej:
                dest_option_string = option_strings[0]
            dest = dest_option_string.lstrip(self.prefix_chars)
            jeżeli nie dest:
                msg = _('dest= jest required dla options like %r')
                podnieś ValueError(msg % option_string)
            dest = dest.replace('-', '_')

        # zwróć the updated keyword arguments
        zwróć dict(kwargs, dest=dest, option_strings=option_strings)

    def _pop_action_class(self, kwargs, default=Nic):
        action = kwargs.pop('action', default)
        zwróć self._registry_get('action', action, action)

    def _get_handler(self):
        # determine function z conflict handler string
        handler_func_name = '_handle_conflict_%s' % self.conflict_handler
        spróbuj:
            zwróć getattr(self, handler_func_name)
        wyjąwszy AttributeError:
            msg = _('invalid conflict_resolution value: %r')
            podnieś ValueError(msg % self.conflict_handler)

    def _check_conflict(self, action):

        # find all options that conflict przy this option
        confl_optionals = []
        dla option_string w action.option_strings:
            jeżeli option_string w self._option_string_actions:
                confl_optional = self._option_string_actions[option_string]
                confl_optionals.append((option_string, confl_optional))

        # resolve any conflicts
        jeżeli confl_optionals:
            conflict_handler = self._get_handler()
            conflict_handler(action, confl_optionals)

    def _handle_conflict_error(self, action, conflicting_actions):
        message = ngettext('conflicting option string: %s',
                           'conflicting option strings: %s',
                           len(conflicting_actions))
        conflict_string = ', '.join([option_string
                                     dla option_string, action
                                     w conflicting_actions])
        podnieś ArgumentError(action, message % conflict_string)

    def _handle_conflict_resolve(self, action, conflicting_actions):

        # remove all conflicting options
        dla option_string, action w conflicting_actions:

            # remove the conflicting option
            action.option_strings.remove(option_string)
            self._option_string_actions.pop(option_string, Nic)

            # jeżeli the option now has no option string, remove it z the
            # container holding it
            jeżeli nie action.option_strings:
                action.container._remove_action(action)


klasa _ArgumentGroup(_ActionsContainer):

    def __init__(self, container, title=Nic, description=Nic, **kwargs):
        # add any missing keyword arguments by checking the container
        update = kwargs.setdefault
        update('conflict_handler', container.conflict_handler)
        update('prefix_chars', container.prefix_chars)
        update('argument_default', container.argument_default)
        super_init = super(_ArgumentGroup, self).__init__
        super_init(description=description, **kwargs)

        # group attributes
        self.title = title
        self._group_actions = []

        # share most attributes przy the container
        self._registries = container._registries
        self._actions = container._actions
        self._option_string_actions = container._option_string_actions
        self._defaults = container._defaults
        self._has_negative_number_optionals = \
            container._has_negative_number_optionals
        self._mutually_exclusive_groups = container._mutually_exclusive_groups

    def _add_action(self, action):
        action = super(_ArgumentGroup, self)._add_action(action)
        self._group_actions.append(action)
        zwróć action

    def _remove_action(self, action):
        super(_ArgumentGroup, self)._remove_action(action)
        self._group_actions.remove(action)


klasa _MutuallyExclusiveGroup(_ArgumentGroup):

    def __init__(self, container, required=Nieprawda):
        super(_MutuallyExclusiveGroup, self).__init__(container)
        self.required = required
        self._container = container

    def _add_action(self, action):
        jeżeli action.required:
            msg = _('mutually exclusive arguments must be optional')
            podnieś ValueError(msg)
        action = self._container._add_action(action)
        self._group_actions.append(action)
        zwróć action

    def _remove_action(self, action):
        self._container._remove_action(action)
        self._group_actions.remove(action)


klasa ArgumentParser(_AttributeHolder, _ActionsContainer):
    """Object dla parsing command line strings into Python objects.

    Keyword Arguments:
        - prog -- The name of the program (default: sys.argv[0])
        - usage -- A usage message (default: auto-generated z arguments)
        - description -- A description of what the program does
        - epilog -- Text following the argument descriptions
        - parents -- Parsers whose arguments should be copied into this one
        - formatter_class -- HelpFormatter klasa dla printing help messages
        - prefix_chars -- Characters that prefix optional arguments
        - fromfile_prefix_chars -- Characters that prefix files containing
            additional arguments
        - argument_default -- The default value dla all arguments
        - conflict_handler -- String indicating how to handle conflicts
        - add_help -- Add a -h/-help option
        - allow_abbrev -- Allow long options to be abbreviated unambiguously
    """

    def __init__(self,
                 prog=Nic,
                 usage=Nic,
                 description=Nic,
                 epilog=Nic,
                 parents=[],
                 formatter_class=HelpFormatter,
                 prefix_chars='-',
                 fromfile_prefix_chars=Nic,
                 argument_default=Nic,
                 conflict_handler='error',
                 add_help=Prawda,
                 allow_abbrev=Prawda):

        superinit = super(ArgumentParser, self).__init__
        superinit(description=description,
                  prefix_chars=prefix_chars,
                  argument_default=argument_default,
                  conflict_handler=conflict_handler)

        # default setting dla prog
        jeżeli prog jest Nic:
            prog = _os.path.basename(_sys.argv[0])

        self.prog = prog
        self.usage = usage
        self.epilog = epilog
        self.formatter_class = formatter_class
        self.fromfile_prefix_chars = fromfile_prefix_chars
        self.add_help = add_help
        self.allow_abbrev = allow_abbrev

        add_group = self.add_argument_group
        self._positionals = add_group(_('positional arguments'))
        self._optionals = add_group(_('optional arguments'))
        self._subparsers = Nic

        # register types
        def identity(string):
            zwróć string
        self.register('type', Nic, identity)

        # add help argument jeżeli necessary
        # (using explicit default to override global argument_default)
        default_prefix = '-' jeżeli '-' w prefix_chars inaczej prefix_chars[0]
        jeżeli self.add_help:
            self.add_argument(
                default_prefix+'h', default_prefix*2+'help',
                action='help', default=SUPPRESS,
                help=_('show this help message oraz exit'))

        # add parent arguments oraz defaults
        dla parent w parents:
            self._add_container_actions(parent)
            spróbuj:
                defaults = parent._defaults
            wyjąwszy AttributeError:
                dalej
            inaczej:
                self._defaults.update(defaults)

    # =======================
    # Pretty __repr__ methods
    # =======================
    def _get_kwargs(self):
        names = [
            'prog',
            'usage',
            'description',
            'formatter_class',
            'conflict_handler',
            'add_help',
        ]
        zwróć [(name, getattr(self, name)) dla name w names]

    # ==================================
    # Optional/Positional adding methods
    # ==================================
    def add_subparsers(self, **kwargs):
        jeżeli self._subparsers jest nie Nic:
            self.error(_('cannot have multiple subparser arguments'))

        # add the parser klasa to the arguments jeżeli it's nie present
        kwargs.setdefault('parser_class', type(self))

        jeżeli 'title' w kwargs albo 'description' w kwargs:
            title = _(kwargs.pop('title', 'subcommands'))
            description = _(kwargs.pop('description', Nic))
            self._subparsers = self.add_argument_group(title, description)
        inaczej:
            self._subparsers = self._positionals

        # prog defaults to the usage message of this parser, skipping
        # optional arguments oraz przy no "usage:" prefix
        jeżeli kwargs.get('prog') jest Nic:
            formatter = self._get_formatter()
            positionals = self._get_positional_actions()
            groups = self._mutually_exclusive_groups
            formatter.add_usage(self.usage, positionals, groups, '')
            kwargs['prog'] = formatter.format_help().strip()

        # create the parsers action oraz add it to the positionals list
        parsers_class = self._pop_action_class(kwargs, 'parsers')
        action = parsers_class(option_strings=[], **kwargs)
        self._subparsers._add_action(action)

        # zwróć the created parsers action
        zwróć action

    def _add_action(self, action):
        jeżeli action.option_strings:
            self._optionals._add_action(action)
        inaczej:
            self._positionals._add_action(action)
        zwróć action

    def _get_optional_actions(self):
        zwróć [action
                dla action w self._actions
                jeżeli action.option_strings]

    def _get_positional_actions(self):
        zwróć [action
                dla action w self._actions
                jeżeli nie action.option_strings]

    # =====================================
    # Command line argument parsing methods
    # =====================================
    def parse_args(self, args=Nic, namespace=Nic):
        args, argv = self.parse_known_args(args, namespace)
        jeżeli argv:
            msg = _('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        zwróć args

    def parse_known_args(self, args=Nic, namespace=Nic):
        jeżeli args jest Nic:
            # args default to the system args
            args = _sys.argv[1:]
        inaczej:
            # make sure that args are mutable
            args = list(args)

        # default Namespace built z parser defaults
        jeżeli namespace jest Nic:
            namespace = Namespace()

        # add any action defaults that aren't present
        dla action w self._actions:
            jeżeli action.dest jest nie SUPPRESS:
                jeżeli nie hasattr(namespace, action.dest):
                    jeżeli action.default jest nie SUPPRESS:
                        setattr(namespace, action.dest, action.default)

        # add any parser defaults that aren't present
        dla dest w self._defaults:
            jeżeli nie hasattr(namespace, dest):
                setattr(namespace, dest, self._defaults[dest])

        # parse the arguments oraz exit jeżeli there are any errors
        spróbuj:
            namespace, args = self._parse_known_args(args, namespace)
            jeżeli hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
                args.extend(getattr(namespace, _UNRECOGNIZED_ARGS_ATTR))
                delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)
            zwróć namespace, args
        wyjąwszy ArgumentError:
            err = _sys.exc_info()[1]
            self.error(str(err))

    def _parse_known_args(self, arg_strings, namespace):
        # replace arg strings that are file references
        jeżeli self.fromfile_prefix_chars jest nie Nic:
            arg_strings = self._read_args_from_files(arg_strings)

        # map all mutually exclusive arguments to the other arguments
        # they can't occur with
        action_conflicts = {}
        dla mutex_group w self._mutually_exclusive_groups:
            group_actions = mutex_group._group_actions
            dla i, mutex_action w enumerate(mutex_group._group_actions):
                conflicts = action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1:])

        # find all option indices, oraz determine the arg_string_pattern
        # which has an 'O' jeżeli there jest an option at an index,
        # an 'A' jeżeli there jest an argument, albo a '-' jeżeli there jest a '--'
        option_string_indices = {}
        arg_string_pattern_parts = []
        arg_strings_iter = iter(arg_strings)
        dla i, arg_string w enumerate(arg_strings_iter):

            # all args after -- are non-options
            jeżeli arg_string == '--':
                arg_string_pattern_parts.append('-')
                dla arg_string w arg_strings_iter:
                    arg_string_pattern_parts.append('A')

            # otherwise, add the arg to the arg strings
            # oraz note the index jeżeli it was an option
            inaczej:
                option_tuple = self._parse_optional(arg_string)
                jeżeli option_tuple jest Nic:
                    pattern = 'A'
                inaczej:
                    option_string_indices[i] = option_tuple
                    pattern = 'O'
                arg_string_pattern_parts.append(pattern)

        # join the pieces together to form the pattern
        arg_strings_pattern = ''.join(arg_string_pattern_parts)

        # converts arg strings to the appropriate oraz then takes the action
        seen_actions = set()
        seen_non_default_actions = set()

        def take_action(action, argument_strings, option_string=Nic):
            seen_actions.add(action)
            argument_values = self._get_values(action, argument_strings)

            # error jeżeli this argument jest nie allowed przy other previously
            # seen arguments, assuming that actions that use the default
            # value don't really count jako "present"
            jeżeli argument_values jest nie action.default:
                seen_non_default_actions.add(action)
                dla conflict_action w action_conflicts.get(action, []):
                    jeżeli conflict_action w seen_non_default_actions:
                        msg = _('not allowed przy argument %s')
                        action_name = _get_action_name(conflict_action)
                        podnieś ArgumentError(action, msg % action_name)

            # take the action jeżeli we didn't receive a SUPPRESS value
            # (e.g. z a default)
            jeżeli argument_values jest nie SUPPRESS:
                action(self, namespace, argument_values, option_string)

        # function to convert arg_strings into an optional action
        def consume_optional(start_index):

            # get the optional identified at this index
            option_tuple = option_string_indices[start_index]
            action, option_string, explicit_arg = option_tuple

            # identify additional optionals w the same arg string
            # (e.g. -xyz jest the same jako -x -y -z jeżeli no args are required)
            match_argument = self._match_argument
            action_tuples = []
            dopóki Prawda:

                # jeżeli we found no optional action, skip it
                jeżeli action jest Nic:
                    extras.append(arg_strings[start_index])
                    zwróć start_index + 1

                # jeżeli there jest an explicit argument, try to match the
                # optional's string arguments to only this
                jeżeli explicit_arg jest nie Nic:
                    arg_count = match_argument(action, 'A')

                    # jeżeli the action jest a single-dash option oraz takes no
                    # arguments, try to parse more single-dash options out
                    # of the tail of the option string
                    chars = self.prefix_chars
                    jeżeli arg_count == 0 oraz option_string[1] nie w chars:
                        action_tuples.append((action, [], option_string))
                        char = option_string[0]
                        option_string = char + explicit_arg[0]
                        new_explicit_arg = explicit_arg[1:] albo Nic
                        optionals_map = self._option_string_actions
                        jeżeli option_string w optionals_map:
                            action = optionals_map[option_string]
                            explicit_arg = new_explicit_arg
                        inaczej:
                            msg = _('ignored explicit argument %r')
                            podnieś ArgumentError(action, msg % explicit_arg)

                    # jeżeli the action expect exactly one argument, we've
                    # successfully matched the option; exit the loop
                    albo_inaczej arg_count == 1:
                        stop = start_index + 1
                        args = [explicit_arg]
                        action_tuples.append((action, args, option_string))
                        przerwij

                    # error jeżeli a double-dash option did nie use the
                    # explicit argument
                    inaczej:
                        msg = _('ignored explicit argument %r')
                        podnieś ArgumentError(action, msg % explicit_arg)

                # jeżeli there jest no explicit argument, try to match the
                # optional's string arguments przy the following strings
                # jeżeli successful, exit the loop
                inaczej:
                    start = start_index + 1
                    selected_patterns = arg_strings_pattern[start:]
                    arg_count = match_argument(action, selected_patterns)
                    stop = start + arg_count
                    args = arg_strings[start:stop]
                    action_tuples.append((action, args, option_string))
                    przerwij

            # add the Optional to the list oraz zwróć the index at which
            # the Optional's string args stopped
            assert action_tuples
            dla action, args, option_string w action_tuples:
                take_action(action, args, option_string)
            zwróć stop

        # the list of Positionals left to be parsed; this jest modified
        # by consume_positionals()
        positionals = self._get_positional_actions()

        # function to convert arg_strings into positional actions
        def consume_positionals(start_index):
            # match jako many Positionals jako possible
            match_partial = self._match_arguments_partial
            selected_pattern = arg_strings_pattern[start_index:]
            arg_counts = match_partial(positionals, selected_pattern)

            # slice off the appropriate arg strings dla each Positional
            # oraz add the Positional oraz its args to the list
            dla action, arg_count w zip(positionals, arg_counts):
                args = arg_strings[start_index: start_index + arg_count]
                start_index += arg_count
                take_action(action, args)

            # slice off the Positionals that we just parsed oraz zwróć the
            # index at which the Positionals' string args stopped
            positionals[:] = positionals[len(arg_counts):]
            zwróć start_index

        # consume Positionals oraz Optionals alternately, until we have
        # dalejed the last option string
        extras = []
        start_index = 0
        jeżeli option_string_indices:
            max_option_string_index = max(option_string_indices)
        inaczej:
            max_option_string_index = -1
        dopóki start_index <= max_option_string_index:

            # consume any Positionals preceding the next option
            next_option_string_index = min([
                index
                dla index w option_string_indices
                jeżeli index >= start_index])
            jeżeli start_index != next_option_string_index:
                positionals_end_index = consume_positionals(start_index)

                # only try to parse the next optional jeżeli we didn't consume
                # the option string during the positionals parsing
                jeżeli positionals_end_index > start_index:
                    start_index = positionals_end_index
                    kontynuuj
                inaczej:
                    start_index = positionals_end_index

            # jeżeli we consumed all the positionals we could oraz we're nie
            # at the index of an option string, there were extra arguments
            jeżeli start_index nie w option_string_indices:
                strings = arg_strings[start_index:next_option_string_index]
                extras.extend(strings)
                start_index = next_option_string_index

            # consume the next optional oraz any arguments dla it
            start_index = consume_optional(start_index)

        # consume any positionals following the last Optional
        stop_index = consume_positionals(start_index)

        # jeżeli we didn't consume all the argument strings, there were extras
        extras.extend(arg_strings[stop_index:])

        # make sure all required actions were present oraz also convert
        # action defaults which were nie given jako arguments
        required_actions = []
        dla action w self._actions:
            jeżeli action nie w seen_actions:
                jeżeli action.required:
                    required_actions.append(_get_action_name(action))
                inaczej:
                    # Convert action default now instead of doing it before
                    # parsing arguments to avoid calling convert functions
                    # twice (which may fail) jeżeli the argument was given, but
                    # only jeżeli it was defined already w the namespace
                    jeżeli (action.default jest nie Nic oraz
                        isinstance(action.default, str) oraz
                        hasattr(namespace, action.dest) oraz
                        action.default jest getattr(namespace, action.dest)):
                        setattr(namespace, action.dest,
                                self._get_value(action, action.default))

        jeżeli required_actions:
            self.error(_('the following arguments are required: %s') %
                       ', '.join(required_actions))

        # make sure all required groups had one option present
        dla group w self._mutually_exclusive_groups:
            jeżeli group.required:
                dla action w group._group_actions:
                    jeżeli action w seen_non_default_actions:
                        przerwij

                # jeżeli no actions were used, report the error
                inaczej:
                    names = [_get_action_name(action)
                             dla action w group._group_actions
                             jeżeli action.help jest nie SUPPRESS]
                    msg = _('one of the arguments %s jest required')
                    self.error(msg % ' '.join(names))

        # zwróć the updated namespace oraz the extra arguments
        zwróć namespace, extras

    def _read_args_from_files(self, arg_strings):
        # expand arguments referencing files
        new_arg_strings = []
        dla arg_string w arg_strings:

            # dla regular arguments, just add them back into the list
            jeżeli nie arg_string albo arg_string[0] nie w self.fromfile_prefix_chars:
                new_arg_strings.append(arg_string)

            # replace arguments referencing files przy the file content
            inaczej:
                spróbuj:
                    przy open(arg_string[1:]) jako args_file:
                        arg_strings = []
                        dla arg_line w args_file.read().splitlines():
                            dla arg w self.convert_arg_line_to_args(arg_line):
                                arg_strings.append(arg)
                        arg_strings = self._read_args_from_files(arg_strings)
                        new_arg_strings.extend(arg_strings)
                wyjąwszy OSError:
                    err = _sys.exc_info()[1]
                    self.error(str(err))

        # zwróć the modified argument list
        zwróć new_arg_strings

    def convert_arg_line_to_args(self, arg_line):
        zwróć [arg_line]

    def _match_argument(self, action, arg_strings_pattern):
        # match the pattern dla this action to the arg strings
        nargs_pattern = self._get_nargs_pattern(action)
        match = _re.match(nargs_pattern, arg_strings_pattern)

        # podnieś an exception jeżeli we weren't able to find a match
        jeżeli match jest Nic:
            nargs_errors = {
                Nic: _('expected one argument'),
                OPTIONAL: _('expected at most one argument'),
                ONE_OR_MORE: _('expected at least one argument'),
            }
            default = ngettext('expected %s argument',
                               'expected %s arguments',
                               action.nargs) % action.nargs
            msg = nargs_errors.get(action.nargs, default)
            podnieś ArgumentError(action, msg)

        # zwróć the number of arguments matched
        zwróć len(match.group(1))

    def _match_arguments_partial(self, actions, arg_strings_pattern):
        # progressively shorten the actions list by slicing off the
        # final actions until we find a match
        result = []
        dla i w range(len(actions), 0, -1):
            actions_slice = actions[:i]
            pattern = ''.join([self._get_nargs_pattern(action)
                               dla action w actions_slice])
            match = _re.match(pattern, arg_strings_pattern)
            jeżeli match jest nie Nic:
                result.extend([len(string) dla string w match.groups()])
                przerwij

        # zwróć the list of arg string counts
        zwróć result

    def _parse_optional(self, arg_string):
        # jeżeli it's an empty string, it was meant to be a positional
        jeżeli nie arg_string:
            zwróć Nic

        # jeżeli it doesn't start przy a prefix, it was meant to be positional
        jeżeli nie arg_string[0] w self.prefix_chars:
            zwróć Nic

        # jeżeli the option string jest present w the parser, zwróć the action
        jeżeli arg_string w self._option_string_actions:
            action = self._option_string_actions[arg_string]
            zwróć action, arg_string, Nic

        # jeżeli it's just a single character, it was meant to be positional
        jeżeli len(arg_string) == 1:
            zwróć Nic

        # jeżeli the option string before the "=" jest present, zwróć the action
        jeżeli '=' w arg_string:
            option_string, explicit_arg = arg_string.split('=', 1)
            jeżeli option_string w self._option_string_actions:
                action = self._option_string_actions[option_string]
                zwróć action, option_string, explicit_arg

        jeżeli self.allow_abbrev:
            # search through all possible prefixes of the option string
            # oraz all actions w the parser dla possible interpretations
            option_tuples = self._get_option_tuples(arg_string)

            # jeżeli multiple actions match, the option string was ambiguous
            jeżeli len(option_tuples) > 1:
                options = ', '.join([option_string
                    dla action, option_string, explicit_arg w option_tuples])
                args = {'option': arg_string, 'matches': options}
                msg = _('ambiguous option: %(option)s could match %(matches)s')
                self.error(msg % args)

            # jeżeli exactly one action matched, this segmentation jest good,
            # so zwróć the parsed action
            albo_inaczej len(option_tuples) == 1:
                option_tuple, = option_tuples
                zwróć option_tuple

        # jeżeli it was nie found jako an option, but it looks like a negative
        # number, it was meant to be positional
        # unless there are negative-number-like options
        jeżeli self._negative_number_matcher.match(arg_string):
            jeżeli nie self._has_negative_number_optionals:
                zwróć Nic

        # jeżeli it contains a space, it was meant to be a positional
        jeżeli ' ' w arg_string:
            zwróć Nic

        # it was meant to be an optional but there jest no such option
        # w this parser (though it might be a valid option w a subparser)
        zwróć Nic, arg_string, Nic

    def _get_option_tuples(self, option_string):
        result = []

        # option strings starting przy two prefix characters are only
        # split at the '='
        chars = self.prefix_chars
        jeżeli option_string[0] w chars oraz option_string[1] w chars:
            jeżeli '=' w option_string:
                option_prefix, explicit_arg = option_string.split('=', 1)
            inaczej:
                option_prefix = option_string
                explicit_arg = Nic
            dla option_string w self._option_string_actions:
                jeżeli option_string.startswith(option_prefix):
                    action = self._option_string_actions[option_string]
                    tup = action, option_string, explicit_arg
                    result.append(tup)

        # single character options can be concatenated przy their arguments
        # but multiple character options always have to have their argument
        # separate
        albo_inaczej option_string[0] w chars oraz option_string[1] nie w chars:
            option_prefix = option_string
            explicit_arg = Nic
            short_option_prefix = option_string[:2]
            short_explicit_arg = option_string[2:]

            dla option_string w self._option_string_actions:
                jeżeli option_string == short_option_prefix:
                    action = self._option_string_actions[option_string]
                    tup = action, option_string, short_explicit_arg
                    result.append(tup)
                albo_inaczej option_string.startswith(option_prefix):
                    action = self._option_string_actions[option_string]
                    tup = action, option_string, explicit_arg
                    result.append(tup)

        # shouldn't ever get here
        inaczej:
            self.error(_('unexpected option string: %s') % option_string)

        # zwróć the collected option tuples
        zwróć result

    def _get_nargs_pattern(self, action):
        # w all examples below, we have to allow dla '--' args
        # which are represented jako '-' w the pattern
        nargs = action.nargs

        # the default (Nic) jest assumed to be a single argument
        jeżeli nargs jest Nic:
            nargs_pattern = '(-*A-*)'

        # allow zero albo one arguments
        albo_inaczej nargs == OPTIONAL:
            nargs_pattern = '(-*A?-*)'

        # allow zero albo more arguments
        albo_inaczej nargs == ZERO_OR_MORE:
            nargs_pattern = '(-*[A-]*)'

        # allow one albo more arguments
        albo_inaczej nargs == ONE_OR_MORE:
            nargs_pattern = '(-*A[A-]*)'

        # allow any number of options albo arguments
        albo_inaczej nargs == REMAINDER:
            nargs_pattern = '([-AO]*)'

        # allow one argument followed by any number of options albo arguments
        albo_inaczej nargs == PARSER:
            nargs_pattern = '(-*A[-AO]*)'

        # all others should be integers
        inaczej:
            nargs_pattern = '(-*%s-*)' % '-*'.join('A' * nargs)

        # jeżeli this jest an optional action, -- jest nie allowed
        jeżeli action.option_strings:
            nargs_pattern = nargs_pattern.replace('-*', '')
            nargs_pattern = nargs_pattern.replace('-', '')

        # zwróć the pattern
        zwróć nargs_pattern

    # ========================
    # Value conversion methods
    # ========================
    def _get_values(self, action, arg_strings):
        # dla everything but PARSER, REMAINDER args, strip out first '--'
        jeżeli action.nargs nie w [PARSER, REMAINDER]:
            spróbuj:
                arg_strings.remove('--')
            wyjąwszy ValueError:
                dalej

        # optional argument produces a default when nie present
        jeżeli nie arg_strings oraz action.nargs == OPTIONAL:
            jeżeli action.option_strings:
                value = action.const
            inaczej:
                value = action.default
            jeżeli isinstance(value, str):
                value = self._get_value(action, value)
                self._check_value(action, value)

        # when nargs='*' on a positional, jeżeli there were no command-line
        # args, use the default jeżeli it jest anything other than Nic
        albo_inaczej (nie arg_strings oraz action.nargs == ZERO_OR_MORE oraz
              nie action.option_strings):
            jeżeli action.default jest nie Nic:
                value = action.default
            inaczej:
                value = arg_strings
            self._check_value(action, value)

        # single argument albo optional argument produces a single value
        albo_inaczej len(arg_strings) == 1 oraz action.nargs w [Nic, OPTIONAL]:
            arg_string, = arg_strings
            value = self._get_value(action, arg_string)
            self._check_value(action, value)

        # REMAINDER arguments convert all values, checking none
        albo_inaczej action.nargs == REMAINDER:
            value = [self._get_value(action, v) dla v w arg_strings]

        # PARSER arguments convert all values, but check only the first
        albo_inaczej action.nargs == PARSER:
            value = [self._get_value(action, v) dla v w arg_strings]
            self._check_value(action, value[0])

        # all other types of nargs produce a list
        inaczej:
            value = [self._get_value(action, v) dla v w arg_strings]
            dla v w value:
                self._check_value(action, v)

        # zwróć the converted value
        zwróć value

    def _get_value(self, action, arg_string):
        type_func = self._registry_get('type', action.type, action.type)
        jeżeli nie callable(type_func):
            msg = _('%r jest nie callable')
            podnieś ArgumentError(action, msg % type_func)

        # convert the value to the appropriate type
        spróbuj:
            result = type_func(arg_string)

        # ArgumentTypeErrors indicate errors
        wyjąwszy ArgumentTypeError:
            name = getattr(action.type, '__name__', repr(action.type))
            msg = str(_sys.exc_info()[1])
            podnieś ArgumentError(action, msg)

        # TypeErrors albo ValueErrors also indicate errors
        wyjąwszy (TypeError, ValueError):
            name = getattr(action.type, '__name__', repr(action.type))
            args = {'type': name, 'value': arg_string}
            msg = _('invalid %(type)s value: %(value)r')
            podnieś ArgumentError(action, msg % args)

        # zwróć the converted value
        zwróć result

    def _check_value(self, action, value):
        # converted value must be one of the choices (jeżeli specified)
        jeżeli action.choices jest nie Nic oraz value nie w action.choices:
            args = {'value': value,
                    'choices': ', '.join(map(repr, action.choices))}
            msg = _('invalid choice: %(value)r (choose z %(choices)s)')
            podnieś ArgumentError(action, msg % args)

    # =======================
    # Help-formatting methods
    # =======================
    def format_usage(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)
        zwróć formatter.format_help()

    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals oraz user-defined groups
        dla action_group w self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help z format above
        zwróć formatter.format_help()

    def _get_formatter(self):
        zwróć self.formatter_class(prog=self.prog)

    # =====================
    # Help-printing methods
    # =====================
    def print_usage(self, file=Nic):
        jeżeli file jest Nic:
            file = _sys.stdout
        self._print_message(self.format_usage(), file)

    def print_help(self, file=Nic):
        jeżeli file jest Nic:
            file = _sys.stdout
        self._print_message(self.format_help(), file)

    def _print_message(self, message, file=Nic):
        jeżeli message:
            jeżeli file jest Nic:
                file = _sys.stderr
            file.write(message)

    # ===============
    # Exiting methods
    # ===============
    def exit(self, status=0, message=Nic):
        jeżeli message:
            self._print_message(message, _sys.stderr)
        _sys.exit(status)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr oraz
        exits.

        If you override this w a subclass, it should nie zwróć -- it
        should either exit albo podnieś an exception.
        """
        self.print_usage(_sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
