"""Configuration file parser.

A configuration file consists of sections, lead by a "[section]" header,
and followed by "name: value" entries, przy continuations oraz such w
the style of RFC 822.

Intrinsic defaults can be specified by dalejing them into the
ConfigParser constructor jako a dictionary.

class:

ConfigParser -- responsible dla parsing a list of
                    configuration files, oraz managing the parsed database.

    methods:

    __init__(defaults=Nic, dict_type=_default_dict, allow_no_value=Nieprawda,
             delimiters=('=', ':'), comment_prefixes=('#', ';'),
             inline_comment_prefixes=Nic, strict=Prawda,
             empty_lines_in_values=Prawda, default_section='DEFAULT',
             interpolation=<unset>, converters=<unset>):
        Create the parser. When `defaults' jest given, it jest initialized into the
        dictionary albo intrinsic defaults. The keys must be strings, the values
        must be appropriate dla %()s string interpolation.

        When `dict_type' jest given, it will be used to create the dictionary
        objects dla the list of sections, dla the options within a section, oraz
        dla the default values.

        When `delimiters' jest given, it will be used jako the set of substrings
        that divide keys z values.

        When `comment_prefixes' jest given, it will be used jako the set of
        substrings that prefix comments w empty lines. Comments can be
        indented.

        When `inline_comment_prefixes' jest given, it will be used jako the set of
        substrings that prefix comments w non-empty lines.

        When `strict` jest Prawda, the parser won't allow dla any section albo option
        duplicates dopóki reading z a single source (file, string albo
        dictionary). Default jest Prawda.

        When `empty_lines_in_values' jest Nieprawda (default: Prawda), each empty line
        marks the end of an option. Otherwise, internal empty lines of
        a multiline option are kept jako part of the value.

        When `allow_no_value' jest Prawda (default: Nieprawda), options without
        values are accepted; the value presented dla these jest Nic.

        When `default_section' jest given, the name of the special section jest
        named accordingly. By default it jest called ``"DEFAULT"`` but this can
        be customized to point to any other valid section name. Its current
        value can be retrieved using the ``parser_instance.default_section``
        attribute oraz may be modified at runtime.

        When `interpolation` jest given, it should be an Interpolation subclass
        instance. It will be used jako the handler dla option value
        pre-processing when using getters. RawConfigParser object s don't do
        any sort of interpolation, whereas ConfigParser uses an instance of
        BasicInterpolation. The library also provides a ``zc.buildbot``
        inspired ExtendedInterpolation implementation.

        When `converters` jest given, it should be a dictionary where each key
        represents the name of a type converter oraz each value jest a callable
        implementing the conversion z string to the desired datatype. Every
        converter gets its corresponding get*() method on the parser object oraz
        section proxies.

    sections()
        Return all the configuration section names, sans DEFAULT.

    has_section(section)
        Return whether the given section exists.

    has_option(section, option)
        Return whether the given option exists w the given section.

    options(section)
        Return list of configuration options dla the named section.

    read(filenames, encoding=Nic)
        Read oraz parse the list of named configuration files, given by
        name.  A single filename jest also allowed.  Non-existing files
        are ignored.  Return list of successfully read files.

    read_file(f, filename=Nic)
        Read oraz parse one configuration file, given jako a file object.
        The filename defaults to f.name; it jest only used w error
        messages (jeżeli f has no `name' attribute, the string `<???>' jest used).

    read_string(string)
        Read configuration z a given string.

    read_dict(dictionary)
        Read configuration z a dictionary. Keys are section names,
        values are dictionaries przy keys oraz values that should be present
        w the section. If the used dictionary type preserves order, sections
        oraz their keys will be added w order. Values are automatically
        converted to strings.

    get(section, option, raw=Nieprawda, vars=Nic, fallback=_UNSET)
        Return a string value dla the named option.  All % interpolations are
        expanded w the zwróć values, based on the defaults dalejed into the
        constructor oraz the DEFAULT section.  Additional substitutions may be
        provided using the `vars' argument, which must be a dictionary whose
        contents override any pre-existing defaults. If `option' jest a key w
        `vars', the value z `vars' jest used.

    getint(section, options, raw=Nieprawda, vars=Nic, fallback=_UNSET)
        Like get(), but convert value to an integer.

    getfloat(section, options, raw=Nieprawda, vars=Nic, fallback=_UNSET)
        Like get(), but convert value to a float.

    getboolean(section, options, raw=Nieprawda, vars=Nic, fallback=_UNSET)
        Like get(), but convert value to a boolean (currently case
        insensitively defined jako 0, false, no, off dla Nieprawda, oraz 1, true,
        yes, on dla Prawda).  Returns Nieprawda albo Prawda.

    items(section=_UNSET, raw=Nieprawda, vars=Nic)
        If section jest given, zwróć a list of tuples przy (name, value) for
        each option w the section. Otherwise, zwróć a list of tuples with
        (section_name, section_proxy) dla each section, including DEFAULTSECT.

    remove_section(section)
        Remove the given file section oraz all its options.

    remove_option(section, option)
        Remove the given option z the given section.

    set(section, option, value)
        Set the given option.

    write(fp, space_around_delimiters=Prawda)
        Write the configuration state w .ini format. If
        `space_around_delimiters' jest Prawda (the default), delimiters
        between keys oraz values are surrounded by spaces.
"""

z collections.abc zaimportuj MutableMapping
z collections zaimportuj OrderedDict jako _default_dict, ChainMap jako _ChainMap
zaimportuj functools
zaimportuj io
zaimportuj itertools
zaimportuj re
zaimportuj sys
zaimportuj warnings

__all__ = ["NoSectionError", "DuplicateOptionError", "DuplicateSectionError",
           "NoOptionError", "InterpolationError", "InterpolationDepthError",
           "InterpolationMissingOptionError", "InterpolationSyntaxError",
           "ParsingError", "MissingSectionHeaderError",
           "ConfigParser", "SafeConfigParser", "RawConfigParser",
           "Interpolation", "BasicInterpolation",  "ExtendedInterpolation",
           "LegacyInterpolation", "SectionProxy", "ConverterMapping",
           "DEFAULTSECT", "MAX_INTERPOLATION_DEPTH"]

DEFAULTSECT = "DEFAULT"

MAX_INTERPOLATION_DEPTH = 10



# exception classes
klasa Error(Exception):
    """Base klasa dla ConfigParser exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        zwróć self.message

    __str__ = __repr__


klasa NoSectionError(Error):
    """Raised when no section matches a requested option."""

    def __init__(self, section):
        Error.__init__(self, 'No section: %r' % (section,))
        self.section = section
        self.args = (section, )


klasa DuplicateSectionError(Error):
    """Raised when a section jest repeated w an input source.

    Possible repetitions that podnieś this exception are: multiple creation
    using the API albo w strict parsers when a section jest found more than once
    w a single input file, string albo dictionary.
    """

    def __init__(self, section, source=Nic, lineno=Nic):
        msg = [repr(section), " already exists"]
        jeżeli source jest nie Nic:
            message = ["While reading z ", repr(source)]
            jeżeli lineno jest nie Nic:
                message.append(" [line {0:2d}]".format(lineno))
            message.append(": section ")
            message.extend(msg)
            msg = message
        inaczej:
            msg.insert(0, "Section ")
        Error.__init__(self, "".join(msg))
        self.section = section
        self.source = source
        self.lineno = lineno
        self.args = (section, source, lineno)


klasa DuplicateOptionError(Error):
    """Raised by strict parsers when an option jest repeated w an input source.

    Current implementation podnieśs this exception only when an option jest found
    more than once w a single file, string albo dictionary.
    """

    def __init__(self, section, option, source=Nic, lineno=Nic):
        msg = [repr(option), " w section ", repr(section),
               " already exists"]
        jeżeli source jest nie Nic:
            message = ["While reading z ", repr(source)]
            jeżeli lineno jest nie Nic:
                message.append(" [line {0:2d}]".format(lineno))
            message.append(": option ")
            message.extend(msg)
            msg = message
        inaczej:
            msg.insert(0, "Option ")
        Error.__init__(self, "".join(msg))
        self.section = section
        self.option = option
        self.source = source
        self.lineno = lineno
        self.args = (section, option, source, lineno)


klasa NoOptionError(Error):
    """A requested option was nie found."""

    def __init__(self, option, section):
        Error.__init__(self, "No option %r w section: %r" %
                       (option, section))
        self.option = option
        self.section = section
        self.args = (option, section)


klasa InterpolationError(Error):
    """Base klasa dla interpolation-related exceptions."""

    def __init__(self, option, section, msg):
        Error.__init__(self, msg)
        self.option = option
        self.section = section
        self.args = (option, section, msg)


klasa InterpolationMissingOptionError(InterpolationError):
    """A string substitution required a setting which was nie available."""

    def __init__(self, option, section, rawval, reference):
        msg = ("Bad value substitution:\n"
               "\tsection: [%s]\n"
               "\toption : %s\n"
               "\tkey    : %s\n"
               "\trawval : %s\n"
               % (section, option, reference, rawval))
        InterpolationError.__init__(self, option, section, msg)
        self.reference = reference
        self.args = (option, section, rawval, reference)


klasa InterpolationSyntaxError(InterpolationError):
    """Raised when the source text contains invalid syntax.

    Current implementation podnieśs this exception when the source text into
    which substitutions are made does nie conform to the required syntax.
    """


klasa InterpolationDepthError(InterpolationError):
    """Raised when substitutions are nested too deeply."""

    def __init__(self, option, section, rawval):
        msg = ("Value interpolation too deeply recursive:\n"
               "\tsection: [%s]\n"
               "\toption : %s\n"
               "\trawval : %s\n"
               % (section, option, rawval))
        InterpolationError.__init__(self, option, section, msg)
        self.args = (option, section, rawval)


klasa ParsingError(Error):
    """Raised when a configuration file does nie follow legal syntax."""

    def __init__(self, source=Nic, filename=Nic):
        # Exactly one of `source'/`filename' arguments has to be given.
        # `filename' kept dla compatibility.
        jeżeli filename oraz source:
            podnieś ValueError("Cannot specify both `filename' oraz `source'. "
                             "Use `source'.")
        albo_inaczej nie filename oraz nie source:
            podnieś ValueError("Required argument `source' nie given.")
        albo_inaczej filename:
            source = filename
        Error.__init__(self, 'Source contains parsing errors: %r' % source)
        self.source = source
        self.errors = []
        self.args = (source, )

    @property
    def filename(self):
        """Deprecated, use `source'."""
        warnings.warn(
            "The 'filename' attribute will be removed w future versions.  "
            "Use 'source' instead.",
            DeprecationWarning, stacklevel=2
        )
        zwróć self.source

    @filename.setter
    def filename(self, value):
        """Deprecated, user `source'."""
        warnings.warn(
            "The 'filename' attribute will be removed w future versions.  "
            "Use 'source' instead.",
            DeprecationWarning, stacklevel=2
        )
        self.source = value

    def append(self, lineno, line):
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)


klasa MissingSectionHeaderError(ParsingError):
    """Raised when a key-value pair jest found before any section header."""

    def __init__(self, filename, lineno, line):
        Error.__init__(
            self,
            'File contains no section headers.\nfile: %r, line: %d\n%r' %
            (filename, lineno, line))
        self.source = filename
        self.lineno = lineno
        self.line = line
        self.args = (filename, lineno, line)


# Used w parser getters to indicate the default behaviour when a specific
# option jest nie found it to podnieś an exception. Created to enable `Nic' as
# a valid fallback value.
_UNSET = object()


klasa Interpolation:
    """Dummy interpolation that dalejes the value through przy no changes."""

    def before_get(self, parser, section, option, value, defaults):
        zwróć value

    def before_set(self, parser, section, option, value):
        zwróć value

    def before_read(self, parser, section, option, value):
        zwróć value

    def before_write(self, parser, section, option, value):
        zwróć value


klasa BasicInterpolation(Interpolation):
    """Interpolation jako implemented w the classic ConfigParser.

    The option values can contain format strings which refer to other values w
    the same section, albo values w the special default section.

    For example:

        something: %(dir)s/whatever

    would resolve the "%(dir)s" to the value of dir.  All reference
    expansions are done late, on demand. If a user needs to use a bare % w
    a configuration file, she can escape it by writing %%. Other % usage
    jest considered a user error oraz podnieśs `InterpolationSyntaxError'."""

    _KEYCRE = re.compile(r"%\(([^)]+)\)s")

    def before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults, 1)
        zwróć ''.join(L)

    def before_set(self, parser, section, option, value):
        tmp_value = value.replace('%%', '') # escaped percent signs
        tmp_value = self._KEYCRE.sub('', tmp_value) # valid syntax
        jeżeli '%' w tmp_value:
            podnieś ValueError("invalid interpolation syntax w %r at "
                             "position %d" % (value, tmp_value.find('%')))
        zwróć value

    def _interpolate_some(self, parser, option, accum, rest, section, map,
                          depth):
        jeżeli depth > MAX_INTERPOLATION_DEPTH:
            podnieś InterpolationDepthError(option, section, rest)
        dopóki rest:
            p = rest.find("%")
            jeżeli p < 0:
                accum.append(rest)
                zwróć
            jeżeli p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p jest no longer used
            c = rest[1:2]
            jeżeli c == "%":
                accum.append("%")
                rest = rest[2:]
            albo_inaczej c == "(":
                m = self._KEYCRE.match(rest)
                jeżeli m jest Nic:
                    podnieś InterpolationSyntaxError(option, section,
                        "bad interpolation variable reference %r" % rest)
                var = parser.optionxform(m.group(1))
                rest = rest[m.end():]
                spróbuj:
                    v = map[var]
                wyjąwszy KeyError:
                    podnieś InterpolationMissingOptionError(
                        option, section, rest, var) z Nic
                jeżeli "%" w v:
                    self._interpolate_some(parser, option, accum, v,
                                           section, map, depth + 1)
                inaczej:
                    accum.append(v)
            inaczej:
                podnieś InterpolationSyntaxError(
                    option, section,
                    "'%%' must be followed by '%%' albo '(', "
                    "found: %r" % (rest,))


klasa ExtendedInterpolation(Interpolation):
    """Advanced variant of interpolation, supports the syntax used by
    `zc.buildout'. Enables interpolation between sections."""

    _KEYCRE = re.compile(r"\$\{([^}]+)\}")

    def before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults, 1)
        zwróć ''.join(L)

    def before_set(self, parser, section, option, value):
        tmp_value = value.replace('$$', '') # escaped dollar signs
        tmp_value = self._KEYCRE.sub('', tmp_value) # valid syntax
        jeżeli '$' w tmp_value:
            podnieś ValueError("invalid interpolation syntax w %r at "
                             "position %d" % (value, tmp_value.find('$')))
        zwróć value

    def _interpolate_some(self, parser, option, accum, rest, section, map,
                          depth):
        jeżeli depth > MAX_INTERPOLATION_DEPTH:
            podnieś InterpolationDepthError(option, section, rest)
        dopóki rest:
            p = rest.find("$")
            jeżeli p < 0:
                accum.append(rest)
                zwróć
            jeżeli p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p jest no longer used
            c = rest[1:2]
            jeżeli c == "$":
                accum.append("$")
                rest = rest[2:]
            albo_inaczej c == "{":
                m = self._KEYCRE.match(rest)
                jeżeli m jest Nic:
                    podnieś InterpolationSyntaxError(option, section,
                        "bad interpolation variable reference %r" % rest)
                path = m.group(1).split(':')
                rest = rest[m.end():]
                sect = section
                opt = option
                spróbuj:
                    jeżeli len(path) == 1:
                        opt = parser.optionxform(path[0])
                        v = map[opt]
                    albo_inaczej len(path) == 2:
                        sect = path[0]
                        opt = parser.optionxform(path[1])
                        v = parser.get(sect, opt, raw=Prawda)
                    inaczej:
                        podnieś InterpolationSyntaxError(
                            option, section,
                            "More than one ':' found: %r" % (rest,))
                wyjąwszy (KeyError, NoSectionError, NoOptionError):
                    podnieś InterpolationMissingOptionError(
                        option, section, rest, ":".join(path)) z Nic
                jeżeli "$" w v:
                    self._interpolate_some(parser, opt, accum, v, sect,
                                           dict(parser.items(sect, raw=Prawda)),
                                           depth + 1)
                inaczej:
                    accum.append(v)
            inaczej:
                podnieś InterpolationSyntaxError(
                    option, section,
                    "'$' must be followed by '$' albo '{', "
                    "found: %r" % (rest,))


klasa LegacyInterpolation(Interpolation):
    """Deprecated interpolation used w old versions of ConfigParser.
    Use BasicInterpolation albo ExtendedInterpolation instead."""

    _KEYCRE = re.compile(r"%\(([^)]*)\)s|.")

    def before_get(self, parser, section, option, value, vars):
        rawval = value
        depth = MAX_INTERPOLATION_DEPTH
        dopóki depth:                    # Loop through this until it's done
            depth -= 1
            jeżeli value oraz "%(" w value:
                replace = functools.partial(self._interpolation_replace,
                                            parser=parser)
                value = self._KEYCRE.sub(replace, value)
                spróbuj:
                    value = value % vars
                wyjąwszy KeyError jako e:
                    podnieś InterpolationMissingOptionError(
                        option, section, rawval, e.args[0]) z Nic
            inaczej:
                przerwij
        jeżeli value oraz "%(" w value:
            podnieś InterpolationDepthError(option, section, rawval)
        zwróć value

    def before_set(self, parser, section, option, value):
        zwróć value

    @staticmethod
    def _interpolation_replace(match, parser):
        s = match.group(1)
        jeżeli s jest Nic:
            zwróć match.group()
        inaczej:
            zwróć "%%(%s)s" % parser.optionxform(s)


klasa RawConfigParser(MutableMapping):
    """ConfigParser that does nie do interpolation."""

    # Regular expressions dla parsing section headers oraz options
    _SECT_TMPL = r"""
        \[                                 # [
        (?P<header>[^]]+)                  # very permissive!
        \]                                 # ]
        """
    _OPT_TMPL = r"""
        (?P<option>.*?)                    # very permissive!
        \s*(?P<vi>{delim})\s*              # any number of space/tab,
                                           # followed by any of the
                                           # allowed delimiters,
                                           # followed by any space/tab
        (?P<value>.*)$                     # everything up to eol
        """
    _OPT_NV_TMPL = r"""
        (?P<option>.*?)                    # very permissive!
        \s*(?:                             # any number of space/tab,
        (?P<vi>{delim})\s*                 # optionally followed by
                                           # any of the allowed
                                           # delimiters, followed by any
                                           # space/tab
        (?P<value>.*))?$                   # everything up to eol
        """
    # Interpolation algorithm to be used jeżeli the user does nie specify another
    _DEFAULT_INTERPOLATION = Interpolation()
    # Compiled regular expression dla matching sections
    SECTCRE = re.compile(_SECT_TMPL, re.VERBOSE)
    # Compiled regular expression dla matching options przy typical separators
    OPTCRE = re.compile(_OPT_TMPL.format(delim="=|:"), re.VERBOSE)
    # Compiled regular expression dla matching options przy optional values
    # delimited using typical separators
    OPTCRE_NV = re.compile(_OPT_NV_TMPL.format(delim="=|:"), re.VERBOSE)
    # Compiled regular expression dla matching leading whitespace w a line
    NONSPACECRE = re.compile(r"\S")
    # Possible boolean values w the configuration.
    BOOLEAN_STATES = {'1': Prawda, 'yes': Prawda, 'true': Prawda, 'on': Prawda,
                      '0': Nieprawda, 'no': Nieprawda, 'false': Nieprawda, 'off': Nieprawda}

    def __init__(self, defaults=Nic, dict_type=_default_dict,
                 allow_no_value=Nieprawda, *, delimiters=('=', ':'),
                 comment_prefixes=('#', ';'), inline_comment_prefixes=Nic,
                 strict=Prawda, empty_lines_in_values=Prawda,
                 default_section=DEFAULTSECT,
                 interpolation=_UNSET, converters=_UNSET):

        self._dict = dict_type
        self._sections = self._dict()
        self._defaults = self._dict()
        self._converters = ConverterMapping(self)
        self._proxies = self._dict()
        self._proxies[default_section] = SectionProxy(self, default_section)
        jeżeli defaults:
            dla key, value w defaults.items():
                self._defaults[self.optionxform(key)] = value
        self._delimiters = tuple(delimiters)
        jeżeli delimiters == ('=', ':'):
            self._optcre = self.OPTCRE_NV jeżeli allow_no_value inaczej self.OPTCRE
        inaczej:
            d = "|".join(re.escape(d) dla d w delimiters)
            jeżeli allow_no_value:
                self._optcre = re.compile(self._OPT_NV_TMPL.format(delim=d),
                                          re.VERBOSE)
            inaczej:
                self._optcre = re.compile(self._OPT_TMPL.format(delim=d),
                                          re.VERBOSE)
        self._comment_prefixes = tuple(comment_prefixes albo ())
        self._inline_comment_prefixes = tuple(inline_comment_prefixes albo ())
        self._strict = strict
        self._allow_no_value = allow_no_value
        self._empty_lines_in_values = empty_lines_in_values
        self.default_section=default_section
        self._interpolation = interpolation
        jeżeli self._interpolation jest _UNSET:
            self._interpolation = self._DEFAULT_INTERPOLATION
        jeżeli self._interpolation jest Nic:
            self._interpolation = Interpolation()
        jeżeli converters jest nie _UNSET:
            self._converters.update(converters)

    def defaults(self):
        zwróć self._defaults

    def sections(self):
        """Return a list of section names, excluding [DEFAULT]"""
        # self._sections will never have [DEFAULT] w it
        zwróć list(self._sections.keys())

    def add_section(self, section):
        """Create a new section w the configuration.

        Raise DuplicateSectionError jeżeli a section by the specified name
        already exists. Raise ValueError jeżeli name jest DEFAULT.
        """
        jeżeli section == self.default_section:
            podnieś ValueError('Invalid section name: %r' % section)

        jeżeli section w self._sections:
            podnieś DuplicateSectionError(section)
        self._sections[section] = self._dict()
        self._proxies[section] = SectionProxy(self, section)

    def has_section(self, section):
        """Indicate whether the named section jest present w the configuration.

        The DEFAULT section jest nie acknowledged.
        """
        zwróć section w self._sections

    def options(self, section):
        """Return a list of option names dla the given section name."""
        spróbuj:
            opts = self._sections[section].copy()
        wyjąwszy KeyError:
            podnieś NoSectionError(section) z Nic
        opts.update(self._defaults)
        zwróć list(opts.keys())

    def read(self, filenames, encoding=Nic):
        """Read oraz parse a filename albo a list of filenames.

        Files that cannot be opened are silently ignored; this jest
        designed so that you can specify a list of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), oraz all existing
        configuration files w the list will be read.  A single
        filename may also be given.

        Return list of successfully read files.
        """
        jeżeli isinstance(filenames, str):
            filenames = [filenames]
        read_ok = []
        dla filename w filenames:
            spróbuj:
                przy open(filename, encoding=encoding) jako fp:
                    self._read(fp, filename)
            wyjąwszy OSError:
                kontynuuj
            read_ok.append(filename)
        zwróć read_ok

    def read_file(self, f, source=Nic):
        """Like read() but the argument must be a file-like object.

        The `f' argument must be iterable, returning one line at a time.
        Optional second argument jest the `source' specifying the name of the
        file being read. If nie given, it jest taken z f.name. If `f' has no
        `name' attribute, `<???>' jest used.
        """
        jeżeli source jest Nic:
            spróbuj:
                source = f.name
            wyjąwszy AttributeError:
                source = '<???>'
        self._read(f, source)

    def read_string(self, string, source='<string>'):
        """Read configuration z a given string."""
        sfile = io.StringIO(string)
        self.read_file(sfile, source)

    def read_dict(self, dictionary, source='<dict>'):
        """Read configuration z a dictionary.

        Keys are section names, values are dictionaries przy keys oraz values
        that should be present w the section. If the used dictionary type
        preserves order, sections oraz their keys will be added w order.

        All types held w the dictionary are converted to strings during
        reading, including section names, option names oraz keys.

        Optional second argument jest the `source' specifying the name of the
        dictionary being read.
        """
        elements_added = set()
        dla section, keys w dictionary.items():
            section = str(section)
            spróbuj:
                self.add_section(section)
            wyjąwszy (DuplicateSectionError, ValueError):
                jeżeli self._strict oraz section w elements_added:
                    podnieś
            elements_added.add(section)
            dla key, value w keys.items():
                key = self.optionxform(str(key))
                jeżeli value jest nie Nic:
                    value = str(value)
                jeżeli self._strict oraz (section, key) w elements_added:
                    podnieś DuplicateOptionError(section, key, source)
                elements_added.add((section, key))
                self.set(section, key, value)

    def readfp(self, fp, filename=Nic):
        """Deprecated, use read_file instead."""
        warnings.warn(
            "This method will be removed w future versions.  "
            "Use 'parser.read_file()' instead.",
            DeprecationWarning, stacklevel=2
        )
        self.read_file(fp, source=filename)

    def get(self, section, option, *, raw=Nieprawda, vars=Nic, fallback=_UNSET):
        """Get an option value dla a given section.

        If `vars' jest provided, it must be a dictionary. The option jest looked up
        w `vars' (jeżeli provided), `section', oraz w `DEFAULTSECT' w that order.
        If the key jest nie found oraz `fallback' jest provided, it jest used as
        a fallback value. `Nic' can be provided jako a `fallback' value.

        If interpolation jest enabled oraz the optional argument `raw' jest Nieprawda,
        all interpolations are expanded w the zwróć values.

        Arguments `raw', `vars', oraz `fallback' are keyword only.

        The section DEFAULT jest special.
        """
        spróbuj:
            d = self._unify_values(section, vars)
        wyjąwszy NoSectionError:
            jeżeli fallback jest _UNSET:
                podnieś
            inaczej:
                zwróć fallback
        option = self.optionxform(option)
        spróbuj:
            value = d[option]
        wyjąwszy KeyError:
            jeżeli fallback jest _UNSET:
                podnieś NoOptionError(option, section)
            inaczej:
                zwróć fallback

        jeżeli raw albo value jest Nic:
            zwróć value
        inaczej:
            zwróć self._interpolation.before_get(self, section, option, value,
                                                  d)

    def _get(self, section, conv, option, **kwargs):
        zwróć conv(self.get(section, option, **kwargs))

    def _get_conv(self, section, option, conv, *, raw=Nieprawda, vars=Nic,
                  fallback=_UNSET, **kwargs):
        spróbuj:
            zwróć self._get(section, conv, option, raw=raw, vars=vars,
                             **kwargs)
        wyjąwszy (NoSectionError, NoOptionError):
            jeżeli fallback jest _UNSET:
                podnieś
            zwróć fallback

    # getint, getfloat oraz getboolean provided directly dla backwards compat
    def getint(self, section, option, *, raw=Nieprawda, vars=Nic,
               fallback=_UNSET, **kwargs):
        zwróć self._get_conv(section, option, int, raw=raw, vars=vars,
                              fallback=fallback, **kwargs)

    def getfloat(self, section, option, *, raw=Nieprawda, vars=Nic,
                 fallback=_UNSET, **kwargs):
        zwróć self._get_conv(section, option, float, raw=raw, vars=vars,
                              fallback=fallback, **kwargs)

    def getboolean(self, section, option, *, raw=Nieprawda, vars=Nic,
                   fallback=_UNSET, **kwargs):
        zwróć self._get_conv(section, option, self._convert_to_boolean,
                              raw=raw, vars=vars, fallback=fallback, **kwargs)

    def items(self, section=_UNSET, raw=Nieprawda, vars=Nic):
        """Return a list of (name, value) tuples dla each option w a section.

        All % interpolations are expanded w the zwróć values, based on the
        defaults dalejed into the constructor, unless the optional argument
        `raw' jest true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        The section DEFAULT jest special.
        """
        jeżeli section jest _UNSET:
            zwróć super().items()
        d = self._defaults.copy()
        spróbuj:
            d.update(self._sections[section])
        wyjąwszy KeyError:
            jeżeli section != self.default_section:
                podnieś NoSectionError(section)
        # Update przy the entry specific variables
        jeżeli vars:
            dla key, value w vars.items():
                d[self.optionxform(key)] = value
        value_getter = lambda option: self._interpolation.before_get(self,
            section, option, d[option], d)
        jeżeli raw:
            value_getter = lambda option: d[option]
        zwróć [(option, value_getter(option)) dla option w d.keys()]

    def popitem(self):
        """Remove a section z the parser oraz zwróć it as
        a (section_name, section_proxy) tuple. If no section jest present, podnieś
        KeyError.

        The section DEFAULT jest never returned because it cannot be removed.
        """
        dla key w self.sections():
            value = self[key]
            usuń self[key]
            zwróć key, value
        podnieś KeyError

    def optionxform(self, optionstr):
        zwróć optionstr.lower()

    def has_option(self, section, option):
        """Check dla the existence of a given option w a given section.
        If the specified `section' jest Nic albo an empty string, DEFAULT jest
        assumed. If the specified `section' does nie exist, returns Nieprawda."""
        jeżeli nie section albo section == self.default_section:
            option = self.optionxform(option)
            zwróć option w self._defaults
        albo_inaczej section nie w self._sections:
            zwróć Nieprawda
        inaczej:
            option = self.optionxform(option)
            zwróć (option w self._sections[section]
                    albo option w self._defaults)

    def set(self, section, option, value=Nic):
        """Set an option."""
        jeżeli value:
            value = self._interpolation.before_set(self, section, option,
                                                   value)
        jeżeli nie section albo section == self.default_section:
            sectdict = self._defaults
        inaczej:
            spróbuj:
                sectdict = self._sections[section]
            wyjąwszy KeyError:
                podnieś NoSectionError(section) z Nic
        sectdict[self.optionxform(option)] = value

    def write(self, fp, space_around_delimiters=Prawda):
        """Write an .ini-format representation of the configuration state.

        If `space_around_delimiters' jest Prawda (the default), delimiters
        between keys oraz values are surrounded by spaces.
        """
        jeżeli space_around_delimiters:
            d = " {} ".format(self._delimiters[0])
        inaczej:
            d = self._delimiters[0]
        jeżeli self._defaults:
            self._write_section(fp, self.default_section,
                                    self._defaults.items(), d)
        dla section w self._sections:
            self._write_section(fp, section,
                                self._sections[section].items(), d)

    def _write_section(self, fp, section_name, section_items, delimiter):
        """Write a single section to the specified `fp'."""
        fp.write("[{}]\n".format(section_name))
        dla key, value w section_items:
            value = self._interpolation.before_write(self, section_name, key,
                                                     value)
            jeżeli value jest nie Nic albo nie self._allow_no_value:
                value = delimiter + str(value).replace('\n', '\n\t')
            inaczej:
                value = ""
            fp.write("{}{}\n".format(key, value))
        fp.write("\n")

    def remove_option(self, section, option):
        """Remove an option."""
        jeżeli nie section albo section == self.default_section:
            sectdict = self._defaults
        inaczej:
            spróbuj:
                sectdict = self._sections[section]
            wyjąwszy KeyError:
                podnieś NoSectionError(section) z Nic
        option = self.optionxform(option)
        existed = option w sectdict
        jeżeli existed:
            usuń sectdict[option]
        zwróć existed

    def remove_section(self, section):
        """Remove a file section."""
        existed = section w self._sections
        jeżeli existed:
            usuń self._sections[section]
            usuń self._proxies[section]
        zwróć existed

    def __getitem__(self, key):
        jeżeli key != self.default_section oraz nie self.has_section(key):
            podnieś KeyError(key)
        zwróć self._proxies[key]

    def __setitem__(self, key, value):
        # To conform przy the mapping protocol, overwrites existing values w
        # the section.

        # XXX this jest nie atomic jeżeli read_dict fails at any point. Then again,
        # no update method w configparser jest atomic w this implementation.
        jeżeli key == self.default_section:
            self._defaults.clear()
        albo_inaczej key w self._sections:
            self._sections[key].clear()
        self.read_dict({key: value})

    def __delitem__(self, key):
        jeżeli key == self.default_section:
            podnieś ValueError("Cannot remove the default section.")
        jeżeli nie self.has_section(key):
            podnieś KeyError(key)
        self.remove_section(key)

    def __contains__(self, key):
        zwróć key == self.default_section albo self.has_section(key)

    def __len__(self):
        zwróć len(self._sections) + 1 # the default section

    def __iter__(self):
        # XXX does it przerwij when underlying container state changed?
        zwróć itertools.chain((self.default_section,), self._sections.keys())

    def _read(self, fp, fpname):
        """Parse a sectioned configuration file.

        Each section w a configuration file contains a header, indicated by
        a name w square brackets (`[]'), plus key/value options, indicated by
        `name' oraz `value' delimited przy a specific substring (`=' albo `:' by
        default).

        Values can span multiple lines, jako long jako they are indented deeper
        than the first line of the value. Depending on the parser's mode, blank
        lines may be treated jako parts of multiline values albo ignored.

        Configuration files may include comments, prefixed by specific
        characters (`#' oraz `;' by default). Comments may appear on their own
        w an otherwise empty line albo may be entered w lines holding values albo
        section names.
        """
        elements_added = set()
        cursect = Nic                        # Nic, albo a dictionary
        sectname = Nic
        optname = Nic
        lineno = 0
        indent_level = 0
        e = Nic                              # Nic, albo an exception
        dla lineno, line w enumerate(fp, start=1):
            comment_start = sys.maxsize
            # strip inline comments
            inline_prefixes = {p: -1 dla p w self._inline_comment_prefixes}
            dopóki comment_start == sys.maxsize oraz inline_prefixes:
                next_prefixes = {}
                dla prefix, index w inline_prefixes.items():
                    index = line.find(prefix, index+1)
                    jeżeli index == -1:
                        kontynuuj
                    next_prefixes[prefix] = index
                    jeżeli index == 0 albo (index > 0 oraz line[index-1].isspace()):
                        comment_start = min(comment_start, index)
                inline_prefixes = next_prefixes
            # strip full line comments
            dla prefix w self._comment_prefixes:
                jeżeli line.strip().startswith(prefix):
                    comment_start = 0
                    przerwij
            jeżeli comment_start == sys.maxsize:
                comment_start = Nic
            value = line[:comment_start].strip()
            jeżeli nie value:
                jeżeli self._empty_lines_in_values:
                    # add empty line to the value, but only jeżeli there was no
                    # comment on the line
                    jeżeli (comment_start jest Nic oraz
                        cursect jest nie Nic oraz
                        optname oraz
                        cursect[optname] jest nie Nic):
                        cursect[optname].append('') # newlines added at join
                inaczej:
                    # empty line marks end of value
                    indent_level = sys.maxsize
                kontynuuj
            # continuation line?
            first_nonspace = self.NONSPACECRE.search(line)
            cur_indent_level = first_nonspace.start() jeżeli first_nonspace inaczej 0
            jeżeli (cursect jest nie Nic oraz optname oraz
                cur_indent_level > indent_level):
                cursect[optname].append(value)
            # a section header albo option header?
            inaczej:
                indent_level = cur_indent_level
                # jest it a section header?
                mo = self.SECTCRE.match(value)
                jeżeli mo:
                    sectname = mo.group('header')
                    jeżeli sectname w self._sections:
                        jeżeli self._strict oraz sectname w elements_added:
                            podnieś DuplicateSectionError(sectname, fpname,
                                                        lineno)
                        cursect = self._sections[sectname]
                        elements_added.add(sectname)
                    albo_inaczej sectname == self.default_section:
                        cursect = self._defaults
                    inaczej:
                        cursect = self._dict()
                        self._sections[sectname] = cursect
                        self._proxies[sectname] = SectionProxy(self, sectname)
                        elements_added.add(sectname)
                    # So sections can't start przy a continuation line
                    optname = Nic
                # no section header w the file?
                albo_inaczej cursect jest Nic:
                    podnieś MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                inaczej:
                    mo = self._optcre.match(value)
                    jeżeli mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        jeżeli nie optname:
                            e = self._handle_error(e, fpname, lineno, line)
                        optname = self.optionxform(optname.rstrip())
                        jeżeli (self._strict oraz
                            (sectname, optname) w elements_added):
                            podnieś DuplicateOptionError(sectname, optname,
                                                       fpname, lineno)
                        elements_added.add((sectname, optname))
                        # This check jest fine because the OPTCRE cannot
                        # match jeżeli it would set optval to Nic
                        jeżeli optval jest nie Nic:
                            optval = optval.strip()
                            cursect[optname] = [optval]
                        inaczej:
                            # valueless option handling
                            cursect[optname] = Nic
                    inaczej:
                        # a non-fatal parsing error occurred. set up the
                        # exception but keep going. the exception will be
                        # podnieśd at the end of the file oraz will contain a
                        # list of all bogus lines
                        e = self._handle_error(e, fpname, lineno, line)
        # jeżeli any parsing errors occurred, podnieś an exception
        jeżeli e:
            podnieś e
        self._join_multiline_values()

    def _join_multiline_values(self):
        defaults = self.default_section, self._defaults
        all_sections = itertools.chain((defaults,),
                                       self._sections.items())
        dla section, options w all_sections:
            dla name, val w options.items():
                jeżeli isinstance(val, list):
                    val = '\n'.join(val).rstrip()
                options[name] = self._interpolation.before_read(self,
                                                                section,
                                                                name, val)

    def _handle_error(self, exc, fpname, lineno, line):
        jeżeli nie exc:
            exc = ParsingError(fpname)
        exc.append(lineno, repr(line))
        zwróć exc

    def _unify_values(self, section, vars):
        """Create a sequence of lookups przy 'vars' taking priority over
        the 'section' which takes priority over the DEFAULTSECT.

        """
        sectiondict = {}
        spróbuj:
            sectiondict = self._sections[section]
        wyjąwszy KeyError:
            jeżeli section != self.default_section:
                podnieś NoSectionError(section)
        # Update przy the entry specific variables
        vardict = {}
        jeżeli vars:
            dla key, value w vars.items():
                jeżeli value jest nie Nic:
                    value = str(value)
                vardict[self.optionxform(key)] = value
        zwróć _ChainMap(vardict, sectiondict, self._defaults)

    def _convert_to_boolean(self, value):
        """Return a boolean value translating z other types jeżeli necessary.
        """
        jeżeli value.lower() nie w self.BOOLEAN_STATES:
            podnieś ValueError('Not a boolean: %s' % value)
        zwróć self.BOOLEAN_STATES[value.lower()]

    def _validate_value_types(self, *, section="", option="", value=""):
        """Raises a TypeError dla non-string values.

        The only legal non-string value jeżeli we allow valueless
        options jest Nic, so we need to check jeżeli the value jest a
        string if:
        - we do nie allow valueless options, albo
        - we allow valueless options but the value jest nie Nic

        For compatibility reasons this method jest nie used w classic set()
        dla RawConfigParsers. It jest invoked w every case dla mapping protocol
        access oraz w ConfigParser.set().
        """
        jeżeli nie isinstance(section, str):
            podnieś TypeError("section names must be strings")
        jeżeli nie isinstance(option, str):
            podnieś TypeError("option keys must be strings")
        jeżeli nie self._allow_no_value albo value:
            jeżeli nie isinstance(value, str):
                podnieś TypeError("option values must be strings")

    @property
    def converters(self):
        zwróć self._converters


klasa ConfigParser(RawConfigParser):
    """ConfigParser implementing interpolation."""

    _DEFAULT_INTERPOLATION = BasicInterpolation()

    def set(self, section, option, value=Nic):
        """Set an option.  Extends RawConfigParser.set by validating type oraz
        interpolation syntax on the value."""
        self._validate_value_types(option=option, value=value)
        super().set(section, option, value)

    def add_section(self, section):
        """Create a new section w the configuration.  Extends
        RawConfigParser.add_section by validating jeżeli the section name jest
        a string."""
        self._validate_value_types(section=section)
        super().add_section(section)


klasa SafeConfigParser(ConfigParser):
    """ConfigParser alias dla backwards compatibility purposes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            "The SafeConfigParser klasa has been renamed to ConfigParser "
            "in Python 3.2. This alias will be removed w future versions."
            " Use ConfigParser directly instead.",
            DeprecationWarning, stacklevel=2
        )


klasa SectionProxy(MutableMapping):
    """A proxy dla a single section z a parser."""

    def __init__(self, parser, name):
        """Creates a view on a section of the specified `name` w `parser`."""
        self._parser = parser
        self._name = name
        dla conv w parser.converters:
            key = 'get' + conv
            getter = functools.partial(self.get, _impl=getattr(parser, key))
            setattr(self, key, getter)

    def __repr__(self):
        zwróć '<Section: {}>'.format(self._name)

    def __getitem__(self, key):
        jeżeli nie self._parser.has_option(self._name, key):
            podnieś KeyError(key)
        zwróć self._parser.get(self._name, key)

    def __setitem__(self, key, value):
        self._parser._validate_value_types(option=key, value=value)
        zwróć self._parser.set(self._name, key, value)

    def __delitem__(self, key):
        jeżeli nie (self._parser.has_option(self._name, key) oraz
                self._parser.remove_option(self._name, key)):
            podnieś KeyError(key)

    def __contains__(self, key):
        zwróć self._parser.has_option(self._name, key)

    def __len__(self):
        zwróć len(self._options())

    def __iter__(self):
        zwróć self._options().__iter__()

    def _options(self):
        jeżeli self._name != self._parser.default_section:
            zwróć self._parser.options(self._name)
        inaczej:
            zwróć self._parser.defaults()

    @property
    def parser(self):
        # The parser object of the proxy jest read-only.
        zwróć self._parser

    @property
    def name(self):
        # The name of the section on a proxy jest read-only.
        zwróć self._name

    def get(self, option, fallback=Nic, *, raw=Nieprawda, vars=Nic,
            _impl=Nic, **kwargs):
        """Get an option value.

        Unless `fallback` jest provided, `Nic` will be returned jeżeli the option
        jest nie found.

        """
        # If `_impl` jest provided, it should be a getter method on the parser
        # object that provides the desired type conversion.
        jeżeli nie _impl:
            _impl = self._parser.get
        zwróć _impl(self._name, option, raw=raw, vars=vars,
                     fallback=fallback, **kwargs)


klasa ConverterMapping(MutableMapping):
    """Enables reuse of get*() methods between the parser oraz section proxies.

    If a parser klasa implements a getter directly, the value dla the given
    key will be ``Nic``. The presence of the converter name here enables
    section proxies to find oraz use the implementation on the parser class.
    """

    GETTERCRE = re.compile(r"^get(?P<name>.+)$")

    def __init__(self, parser):
        self._parser = parser
        self._data = {}
        dla getter w dir(self._parser):
            m = self.GETTERCRE.match(getter)
            jeżeli nie m albo nie callable(getattr(self._parser, getter)):
                kontynuuj
            self._data[m.group('name')] = Nic   # See klasa docstring.

    def __getitem__(self, key):
        zwróć self._data[key]

    def __setitem__(self, key, value):
        spróbuj:
            k = 'get' + key
        wyjąwszy TypeError:
            podnieś ValueError('Incompatible key: {} (type: {})'
                             ''.format(key, type(key)))
        jeżeli k == 'get':
            podnieś ValueError('Incompatible key: cannot use "" jako a name')
        self._data[key] = value
        func = functools.partial(self._parser._get_conv, conv=value)
        func.converter = value
        setattr(self._parser, k, func)
        dla proxy w self._parser.values():
            getter = functools.partial(proxy.get, _impl=func)
            setattr(proxy, k, getter)

    def __delitem__(self, key):
        spróbuj:
            k = 'get' + (key albo Nic)
        wyjąwszy TypeError:
            podnieś KeyError(key)
        usuń self._data[key]
        dla inst w itertools.chain((self._parser,), self._parser.values()):
            spróbuj:
                delattr(inst, k)
            wyjąwszy AttributeError:
                # don't podnieś since the entry was present w _data, silently
                # clean up
                kontynuuj

    def __iter__(self):
        zwróć iter(self._data)

    def __len__(self):
        zwróć len(self._data)
