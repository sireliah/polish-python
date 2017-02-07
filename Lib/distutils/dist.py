"""distutils.dist

Provides the Distribution class, which represents the module distribution
being built/installed/distributed.
"""

zaimportuj sys
zaimportuj os
zaimportuj re
z email zaimportuj message_from_file

spróbuj:
    zaimportuj warnings
wyjąwszy ImportError:
    warnings = Nic

z distutils.errors zaimportuj *
z distutils.fancy_getopt zaimportuj FancyGetopt, translate_longopt
z distutils.util zaimportuj check_environ, strtobool, rfc822_escape
z distutils zaimportuj log
z distutils.debug zaimportuj DEBUG

# Regex to define acceptable Distutils command names.  This jest nie *quite*
# the same jako a Python NAME -- I don't allow leading underscores.  The fact
# that they're very similar jest no coincidence; the default naming scheme jest
# to look dla a Python module named after the command.
command_re = re.compile(r'^[a-zA-Z]([a-zA-Z0-9_]*)$')


klasa Distribution:
    """The core of the Distutils.  Most of the work hiding behind 'setup'
    jest really done within a Distribution instance, which farms the work out
    to the Distutils commands specified on the command line.

    Setup scripts will almost never instantiate Distribution directly,
    unless the 'setup()' function jest totally inadequate to their needs.
    However, it jest conceivable that a setup script might wish to subclass
    Distribution dla some specialized purpose, oraz then dalej the subclass
    to 'setup()' jako the 'distclass' keyword argument.  If so, it jest
    necessary to respect the expectations that 'setup' has of Distribution.
    See the code dla 'setup()', w core.py, dla details.
    """

    # 'global_options' describes the command-line options that may be
    # supplied to the setup script prior to any actual commands.
    # Eg. "./setup.py -n" albo "./setup.py --quiet" both take advantage of
    # these global options.  This list should be kept to a bare minimum,
    # since every global option jest also valid jako a command option -- oraz we
    # don't want to pollute the commands przy too many options that they
    # have minimal control over.
    # The fourth entry dla verbose means that it can be repeated.
    global_options = [
        ('verbose', 'v', "run verbosely (default)", 1),
        ('quiet', 'q', "run quietly (turns verbosity off)"),
        ('dry-run', 'n', "don't actually do anything"),
        ('help', 'h', "show detailed help message"),
        ('no-user-cfg', Nic,
            'ignore pydistutils.cfg w your home directory'),
    ]

    # 'common_usage' jest a short (2-3 line) string describing the common
    # usage of the setup script.
    common_usage = """\
Common commands: (see '--help-commands' dla more)

  setup.py build      will build the package underneath 'build/'
  setup.py install    will install the package
"""

    # options that are nie propagated to the commands
    display_options = [
        ('help-commands', Nic,
         "list all available commands"),
        ('name', Nic,
         "print package name"),
        ('version', 'V',
         "print package version"),
        ('fullname', Nic,
         "print <package name>-<version>"),
        ('author', Nic,
         "print the author's name"),
        ('author-email', Nic,
         "print the author's email address"),
        ('maintainer', Nic,
         "print the maintainer's name"),
        ('maintainer-email', Nic,
         "print the maintainer's email address"),
        ('contact', Nic,
         "print the maintainer's name jeżeli known, inaczej the author's"),
        ('contact-email', Nic,
         "print the maintainer's email address jeżeli known, inaczej the author's"),
        ('url', Nic,
         "print the URL dla this package"),
        ('license', Nic,
         "print the license of the package"),
        ('licence', Nic,
         "alias dla --license"),
        ('description', Nic,
         "print the package description"),
        ('long-description', Nic,
         "print the long package description"),
        ('platforms', Nic,
         "print the list of platforms"),
        ('classifiers', Nic,
         "print the list of classifiers"),
        ('keywords', Nic,
         "print the list of keywords"),
        ('provides', Nic,
         "print the list of packages/modules provided"),
        ('requires', Nic,
         "print the list of packages/modules required"),
        ('obsoletes', Nic,
         "print the list of packages/modules made obsolete")
        ]
    display_option_names = [translate_longopt(x[0]) dla x w display_options]

    # negative options are options that exclude other options
    negative_opt = {'quiet': 'verbose'}

    # -- Creation/initialization methods -------------------------------

    def __init__(self, attrs=Nic):
        """Construct a new Distribution instance: initialize all the
        attributes of a Distribution, oraz then use 'attrs' (a dictionary
        mapping attribute names to values) to assign some of those
        attributes their "real" values.  (Any attributes nie mentioned w
        'attrs' will be assigned to some null value: 0, Nic, an empty list
        albo dictionary, etc.)  Most importantly, initialize the
        'command_obj' attribute to the empty dictionary; this will be
        filled w przy real command objects by 'parse_command_line()'.
        """

        # Default values dla our command-line options
        self.verbose = 1
        self.dry_run = 0
        self.help = 0
        dla attr w self.display_option_names:
            setattr(self, attr, 0)

        # Store the distribution meta-data (name, version, author, oraz so
        # forth) w a separate object -- we're getting to have enough
        # information here (and enough command-line options) that it's
        # worth it.  Also delegate 'get_XXX()' methods to the 'metadata'
        # object w a sneaky oraz underhanded (but efficient!) way.
        self.metadata = DistributionMetadata()
        dla basename w self.metadata._METHOD_BASENAMES:
            method_name = "get_" + basename
            setattr(self, method_name, getattr(self.metadata, method_name))

        # 'cmdclass' maps command names to klasa objects, so we
        # can 1) quickly figure out which klasa to instantiate when
        # we need to create a new command object, oraz 2) have a way
        # dla the setup script to override command classes
        self.cmdclass = {}

        # 'command_packages' jest a list of packages w which commands
        # are searched for.  The factory dla command 'foo' jest expected
        # to be named 'foo' w the module 'foo' w one of the packages
        # named here.  This list jest searched z the left; an error
        # jest podnieśd jeżeli no named package provides the command being
        # searched for.  (Always access using get_command_packages().)
        self.command_packages = Nic

        # 'script_name' oraz 'script_args' are usually set to sys.argv[0]
        # oraz sys.argv[1:], but they can be overridden when the caller jest
        # nie necessarily a setup script run z the command-line.
        self.script_name = Nic
        self.script_args = Nic

        # 'command_options' jest where we store command options between
        # parsing them (z config files, the command-line, etc.) oraz when
        # they are actually needed -- ie. when the command w question jest
        # instantiated.  It jest a dictionary of dictionaries of 2-tuples:
        #   command_options = { command_name : { option : (source, value) } }
        self.command_options = {}

        # 'dist_files' jest the list of (command, pyversion, file) that
        # have been created by any dist commands run so far. This jest
        # filled regardless of whether the run jest dry albo not. pyversion
        # gives sysconfig.get_python_version() jeżeli the dist file jest
        # specific to a Python version, 'any' jeżeli it jest good dla all
        # Python versions on the target platform, oraz '' dla a source
        # file. pyversion should nie be used to specify minimum albo
        # maximum required Python versions; use the metainfo dla that
        # instead.
        self.dist_files = []

        # These options are really the business of various commands, rather
        # than of the Distribution itself.  We provide aliases dla them w
        # Distribution jako a convenience to the developer.
        self.packages = Nic
        self.package_data = {}
        self.package_dir = Nic
        self.py_modules = Nic
        self.libraries = Nic
        self.headers = Nic
        self.ext_modules = Nic
        self.ext_package = Nic
        self.include_dirs = Nic
        self.extra_path = Nic
        self.scripts = Nic
        self.data_files = Nic
        self.password = ''

        # And now initialize bookkeeping stuff that can't be supplied by
        # the caller at all.  'command_obj' maps command names to
        # Command instances -- that's how we enforce that every command
        # klasa jest a singleton.
        self.command_obj = {}

        # 'have_run' maps command names to boolean values; it keeps track
        # of whether we have actually run a particular command, to make it
        # cheap to "run" a command whenever we think we might need to -- if
        # it's already been done, no need dla expensive filesystem
        # operations, we just check the 'have_run' dictionary oraz carry on.
        # It's only safe to query 'have_run' dla a command klasa that has
        # been instantiated -- a false value will be inserted when the
        # command object jest created, oraz replaced przy a true value when
        # the command jest successfully run.  Thus it's probably best to use
        # '.get()' rather than a straight lookup.
        self.have_run = {}

        # Now we'll use the attrs dictionary (ultimately, keyword args from
        # the setup script) to possibly override any albo all of these
        # distribution options.

        jeżeli attrs:
            # Pull out the set of command options oraz work on them
            # specifically.  Note that this order guarantees that aliased
            # command options will override any supplied redundantly
            # through the general options dictionary.
            options = attrs.get('options')
            jeżeli options jest nie Nic:
                usuń attrs['options']
                dla (command, cmd_options) w options.items():
                    opt_dict = self.get_option_dict(command)
                    dla (opt, val) w cmd_options.items():
                        opt_dict[opt] = ("setup script", val)

            jeżeli 'licence' w attrs:
                attrs['license'] = attrs['licence']
                usuń attrs['licence']
                msg = "'licence' distribution option jest deprecated; use 'license'"
                jeżeli warnings jest nie Nic:
                    warnings.warn(msg)
                inaczej:
                    sys.stderr.write(msg + "\n")

            # Now work on the rest of the attributes.  Any attribute that's
            # nie already defined jest invalid!
            dla (key, val) w attrs.items():
                jeżeli hasattr(self.metadata, "set_" + key):
                    getattr(self.metadata, "set_" + key)(val)
                albo_inaczej hasattr(self.metadata, key):
                    setattr(self.metadata, key, val)
                albo_inaczej hasattr(self, key):
                    setattr(self, key, val)
                inaczej:
                    msg = "Unknown distribution option: %s" % repr(key)
                    jeżeli warnings jest nie Nic:
                        warnings.warn(msg)
                    inaczej:
                        sys.stderr.write(msg + "\n")

        # no-user-cfg jest handled before other command line args
        # because other args override the config files, oraz this
        # one jest needed before we can load the config files.
        # If attrs['script_args'] wasn't dalejed, assume false.
        #
        # This also make sure we just look at the global options
        self.want_user_cfg = Prawda

        jeżeli self.script_args jest nie Nic:
            dla arg w self.script_args:
                jeżeli nie arg.startswith('-'):
                    przerwij
                jeżeli arg == '--no-user-cfg':
                    self.want_user_cfg = Nieprawda
                    przerwij

        self.finalize_options()

    def get_option_dict(self, command):
        """Get the option dictionary dla a given command.  If that
        command's option dictionary hasn't been created yet, then create it
        oraz zwróć the new dictionary; otherwise, zwróć the existing
        option dictionary.
        """
        dict = self.command_options.get(command)
        jeżeli dict jest Nic:
            dict = self.command_options[command] = {}
        zwróć dict

    def dump_option_dicts(self, header=Nic, commands=Nic, indent=""):
        z pprint zaimportuj pformat

        jeżeli commands jest Nic:             # dump all command option dicts
            commands = sorted(self.command_options.keys())

        jeżeli header jest nie Nic:
            self.announce(indent + header)
            indent = indent + "  "

        jeżeli nie commands:
            self.announce(indent + "no commands known yet")
            zwróć

        dla cmd_name w commands:
            opt_dict = self.command_options.get(cmd_name)
            jeżeli opt_dict jest Nic:
                self.announce(indent +
                              "no option dict dla '%s' command" % cmd_name)
            inaczej:
                self.announce(indent +
                              "option dict dla '%s' command:" % cmd_name)
                out = pformat(opt_dict)
                dla line w out.split('\n'):
                    self.announce(indent + "  " + line)

    # -- Config file finding/parsing methods ---------------------------

    def find_config_files(self):
        """Find jako many configuration files jako should be processed dla this
        platform, oraz zwróć a list of filenames w the order w which they
        should be parsed.  The filenames returned are guaranteed to exist
        (modulo nasty race conditions).

        There are three possible config files: distutils.cfg w the
        Distutils installation directory (ie. where the top-level
        Distutils __inst__.py file lives), a file w the user's home
        directory named .pydistutils.cfg on Unix oraz pydistutils.cfg
        on Windows/Mac; oraz setup.cfg w the current directory.

        The file w the user's home directory can be disabled przy the
        --no-user-cfg option.
        """
        files = []
        check_environ()

        # Where to look dla the system-wide Distutils config file
        sys_dir = os.path.dirname(sys.modules['distutils'].__file__)

        # Look dla the system config file
        sys_file = os.path.join(sys_dir, "distutils.cfg")
        jeżeli os.path.isfile(sys_file):
            files.append(sys_file)

        # What to call the per-user config file
        jeżeli os.name == 'posix':
            user_filename = ".pydistutils.cfg"
        inaczej:
            user_filename = "pydistutils.cfg"

        # And look dla the user config file
        jeżeli self.want_user_cfg:
            user_file = os.path.join(os.path.expanduser('~'), user_filename)
            jeżeli os.path.isfile(user_file):
                files.append(user_file)

        # All platforms support local setup.cfg
        local_file = "setup.cfg"
        jeżeli os.path.isfile(local_file):
            files.append(local_file)

        jeżeli DEBUG:
            self.announce("using config files: %s" % ', '.join(files))

        zwróć files

    def parse_config_files(self, filenames=Nic):
        z configparser zaimportuj ConfigParser

        # Ignore install directory options jeżeli we have a venv
        jeżeli sys.prefix != sys.base_prefix:
            ignore_options = [
                'install-base', 'install-platbase', 'install-lib',
                'install-platlib', 'install-purelib', 'install-headers',
                'install-scripts', 'install-data', 'prefix', 'exec-prefix',
                'home', 'user', 'root']
        inaczej:
            ignore_options = []

        ignore_options = frozenset(ignore_options)

        jeżeli filenames jest Nic:
            filenames = self.find_config_files()

        jeżeli DEBUG:
            self.announce("Distribution.parse_config_files():")

        parser = ConfigParser()
        dla filename w filenames:
            jeżeli DEBUG:
                self.announce("  reading %s" % filename)
            parser.read(filename)
            dla section w parser.sections():
                options = parser.options(section)
                opt_dict = self.get_option_dict(section)

                dla opt w options:
                    jeżeli opt != '__name__' oraz opt nie w ignore_options:
                        val = parser.get(section,opt)
                        opt = opt.replace('-', '_')
                        opt_dict[opt] = (filename, val)

            # Make the ConfigParser forget everything (so we retain
            # the original filenames that options come from)
            parser.__init__()

        # If there was a "global" section w the config file, use it
        # to set Distribution options.

        jeżeli 'global' w self.command_options:
            dla (opt, (src, val)) w self.command_options['global'].items():
                alias = self.negative_opt.get(opt)
                spróbuj:
                    jeżeli alias:
                        setattr(self, alias, nie strtobool(val))
                    albo_inaczej opt w ('verbose', 'dry_run'): # ugh!
                        setattr(self, opt, strtobool(val))
                    inaczej:
                        setattr(self, opt, val)
                wyjąwszy ValueError jako msg:
                    podnieś DistutilsOptionError(msg)

    # -- Command-line parsing methods ----------------------------------

    def parse_command_line(self):
        """Parse the setup script's command line, taken z the
        'script_args' instance attribute (which defaults to 'sys.argv[1:]'
        -- see 'setup()' w core.py).  This list jest first processed for
        "global options" -- options that set attributes of the Distribution
        instance.  Then, it jest alternately scanned dla Distutils commands
        oraz options dla that command.  Each new command terminates the
        options dla the previous command.  The allowed options dla a
        command are determined by the 'user_options' attribute of the
        command klasa -- thus, we have to be able to load command classes
        w order to parse the command line.  Any error w that 'options'
        attribute podnieśs DistutilsGetoptError; any error on the
        command-line podnieśs DistutilsArgError.  If no Distutils commands
        were found on the command line, podnieśs DistutilsArgError.  Return
        true jeżeli command-line was successfully parsed oraz we should carry
        on przy executing commands; false jeżeli no errors but we shouldn't
        execute commands (currently, this only happens jeżeli user asks for
        help).
        """
        #
        # We now have enough information to show the Macintosh dialog
        # that allows the user to interactively specify the "command line".
        #
        toplevel_options = self._get_toplevel_options()

        # We have to parse the command line a bit at a time -- global
        # options, then the first command, then its options, oraz so on --
        # because each command will be handled by a different class, oraz
        # the options that are valid dla a particular klasa aren't known
        # until we have loaded the command class, which doesn't happen
        # until we know what the command is.

        self.commands = []
        parser = FancyGetopt(toplevel_options + self.display_options)
        parser.set_negative_aliases(self.negative_opt)
        parser.set_aliases({'licence': 'license'})
        args = parser.getopt(args=self.script_args, object=self)
        option_order = parser.get_option_order()
        log.set_verbosity(self.verbose)

        # dla display options we zwróć immediately
        jeżeli self.handle_display_options(option_order):
            zwróć
        dopóki args:
            args = self._parse_command_opts(parser, args)
            jeżeli args jest Nic:            # user asked dla help (and got it)
                zwróć

        # Handle the cases of --help jako a "global" option, ie.
        # "setup.py --help" oraz "setup.py --help command ...".  For the
        # former, we show global options (--verbose, --dry-run, etc.)
        # oraz display-only options (--name, --version, etc.); dla the
        # latter, we omit the display-only options oraz show help for
        # each command listed on the command line.
        jeżeli self.help:
            self._show_help(parser,
                            display_options=len(self.commands) == 0,
                            commands=self.commands)
            zwróć

        # Oops, no commands found -- an end-user error
        jeżeli nie self.commands:
            podnieś DistutilsArgError("no commands supplied")

        # All jest well: zwróć true
        zwróć Prawda

    def _get_toplevel_options(self):
        """Return the non-display options recognized at the top level.

        This includes options that are recognized *only* at the top
        level jako well jako options recognized dla commands.
        """
        zwróć self.global_options + [
            ("command-packages=", Nic,
             "list of packages that provide distutils commands"),
            ]

    def _parse_command_opts(self, parser, args):
        """Parse the command-line options dla a single command.
        'parser' must be a FancyGetopt instance; 'args' must be the list
        of arguments, starting przy the current command (whose options
        we are about to parse).  Returns a new version of 'args' with
        the next command at the front of the list; will be the empty
        list jeżeli there are no more commands on the command line.  Returns
        Nic jeżeli the user asked dla help on this command.
        """
        # late zaimportuj because of mutual dependence between these modules
        z distutils.cmd zaimportuj Command

        # Pull the current command z the head of the command line
        command = args[0]
        jeżeli nie command_re.match(command):
            podnieś SystemExit("invalid command name '%s'" % command)
        self.commands.append(command)

        # Dig up the command klasa that implements this command, so we
        # 1) know that it's a valid command, oraz 2) know which options
        # it takes.
        spróbuj:
            cmd_class = self.get_command_class(command)
        wyjąwszy DistutilsModuleError jako msg:
            podnieś DistutilsArgError(msg)

        # Require that the command klasa be derived z Command -- want
        # to be sure that the basic "command" interface jest implemented.
        jeżeli nie issubclass(cmd_class, Command):
            podnieś DistutilsClassError(
                "command klasa %s must subclass Command" % cmd_class)

        # Also make sure that the command object provides a list of its
        # known options.
        jeżeli nie (hasattr(cmd_class, 'user_options') oraz
                isinstance(cmd_class.user_options, list)):
            msg = ("command klasa %s must provide "
                "'user_options' attribute (a list of tuples)")
            podnieś DistutilsClassError(msg % cmd_class)

        # If the command klasa has a list of negative alias options,
        # merge it w przy the global negative aliases.
        negative_opt = self.negative_opt
        jeżeli hasattr(cmd_class, 'negative_opt'):
            negative_opt = negative_opt.copy()
            negative_opt.update(cmd_class.negative_opt)

        # Check dla help_options w command class.  They have a different
        # format (tuple of four) so we need to preprocess them here.
        jeżeli (hasattr(cmd_class, 'help_options') oraz
                isinstance(cmd_class.help_options, list)):
            help_options = fix_help_options(cmd_class.help_options)
        inaczej:
            help_options = []

        # All commands support the global options too, just by adding
        # w 'global_options'.
        parser.set_option_table(self.global_options +
                                cmd_class.user_options +
                                help_options)
        parser.set_negative_aliases(negative_opt)
        (args, opts) = parser.getopt(args[1:])
        jeżeli hasattr(opts, 'help') oraz opts.help:
            self._show_help(parser, display_options=0, commands=[cmd_class])
            zwróć

        jeżeli (hasattr(cmd_class, 'help_options') oraz
                isinstance(cmd_class.help_options, list)):
            help_option_found=0
            dla (help_option, short, desc, func) w cmd_class.help_options:
                jeżeli hasattr(opts, parser.get_attr_name(help_option)):
                    help_option_found=1
                    jeżeli callable(func):
                        func()
                    inaczej:
                        podnieś DistutilsClassError(
                            "invalid help function %r dla help option '%s': "
                            "must be a callable object (function, etc.)"
                            % (func, help_option))

            jeżeli help_option_found:
                zwróć

        # Put the options z the command-line into their official
        # holding pen, the 'command_options' dictionary.
        opt_dict = self.get_option_dict(command)
        dla (name, value) w vars(opts).items():
            opt_dict[name] = ("command line", value)

        zwróć args

    def finalize_options(self):
        """Set final values dla all the options on the Distribution
        instance, analogous to the .finalize_options() method of Command
        objects.
        """
        dla attr w ('keywords', 'platforms'):
            value = getattr(self.metadata, attr)
            jeżeli value jest Nic:
                kontynuuj
            jeżeli isinstance(value, str):
                value = [elm.strip() dla elm w value.split(',')]
                setattr(self.metadata, attr, value)

    def _show_help(self, parser, global_options=1, display_options=1,
                   commands=[]):
        """Show help dla the setup script command-line w the form of
        several lists of command-line options.  'parser' should be a
        FancyGetopt instance; do nie expect it to be returned w the
        same state, jako its option table will be reset to make it
        generate the correct help text.

        If 'global_options' jest true, lists the global options:
        --verbose, --dry-run, etc.  If 'display_options' jest true, lists
        the "display-only" options: --name, --version, etc.  Finally,
        lists per-command help dla every command name albo command class
        w 'commands'.
        """
        # late zaimportuj because of mutual dependence between these modules
        z distutils.core zaimportuj gen_usage
        z distutils.cmd zaimportuj Command

        jeżeli global_options:
            jeżeli display_options:
                options = self._get_toplevel_options()
            inaczej:
                options = self.global_options
            parser.set_option_table(options)
            parser.print_help(self.common_usage + "\nGlobal options:")
            print('')

        jeżeli display_options:
            parser.set_option_table(self.display_options)
            parser.print_help(
                "Information display options (just display " +
                "information, ignore any commands)")
            print('')

        dla command w self.commands:
            jeżeli isinstance(command, type) oraz issubclass(command, Command):
                klass = command
            inaczej:
                klass = self.get_command_class(command)
            jeżeli (hasattr(klass, 'help_options') oraz
                    isinstance(klass.help_options, list)):
                parser.set_option_table(klass.user_options +
                                        fix_help_options(klass.help_options))
            inaczej:
                parser.set_option_table(klass.user_options)
            parser.print_help("Options dla '%s' command:" % klass.__name__)
            print('')

        print(gen_usage(self.script_name))

    def handle_display_options(self, option_order):
        """If there were any non-global "display-only" options
        (--help-commands albo the metadata display options) on the command
        line, display the requested info oraz zwróć true; inaczej zwróć
        false.
        """
        z distutils.core zaimportuj gen_usage

        # User just wants a list of commands -- we'll print it out oraz stop
        # processing now (ie. jeżeli they ran "setup --help-commands foo bar",
        # we ignore "foo bar").
        jeżeli self.help_commands:
            self.print_commands()
            print('')
            print(gen_usage(self.script_name))
            zwróć 1

        # If user supplied any of the "display metadata" options, then
        # display that metadata w the order w which the user supplied the
        # metadata options.
        any_display_options = 0
        is_display_option = {}
        dla option w self.display_options:
            is_display_option[option[0]] = 1

        dla (opt, val) w option_order:
            jeżeli val oraz is_display_option.get(opt):
                opt = translate_longopt(opt)
                value = getattr(self.metadata, "get_"+opt)()
                jeżeli opt w ['keywords', 'platforms']:
                    print(','.join(value))
                albo_inaczej opt w ('classifiers', 'provides', 'requires',
                             'obsoletes'):
                    print('\n'.join(value))
                inaczej:
                    print(value)
                any_display_options = 1

        zwróć any_display_options

    def print_command_list(self, commands, header, max_length):
        """Print a subset of the list of all commands -- used by
        'print_commands()'.
        """
        print(header + ":")

        dla cmd w commands:
            klass = self.cmdclass.get(cmd)
            jeżeli nie klass:
                klass = self.get_command_class(cmd)
            spróbuj:
                description = klass.description
            wyjąwszy AttributeError:
                description = "(no description available)"

            print("  %-*s  %s" % (max_length, cmd, description))

    def print_commands(self):
        """Print out a help message listing all available commands przy a
        description of each.  The list jest divided into "standard commands"
        (listed w distutils.command.__all__) oraz "extra commands"
        (mentioned w self.cmdclass, but nie a standard command).  The
        descriptions come z the command klasa attribute
        'description'.
        """
        zaimportuj distutils.command
        std_commands = distutils.command.__all__
        is_std = {}
        dla cmd w std_commands:
            is_std[cmd] = 1

        extra_commands = []
        dla cmd w self.cmdclass.keys():
            jeżeli nie is_std.get(cmd):
                extra_commands.append(cmd)

        max_length = 0
        dla cmd w (std_commands + extra_commands):
            jeżeli len(cmd) > max_length:
                max_length = len(cmd)

        self.print_command_list(std_commands,
                                "Standard commands",
                                max_length)
        jeżeli extra_commands:
            print()
            self.print_command_list(extra_commands,
                                    "Extra commands",
                                    max_length)

    def get_command_list(self):
        """Get a list of (command, description) tuples.
        The list jest divided into "standard commands" (listed w
        distutils.command.__all__) oraz "extra commands" (mentioned w
        self.cmdclass, but nie a standard command).  The descriptions come
        z the command klasa attribute 'description'.
        """
        # Currently this jest only used on Mac OS, dla the Mac-only GUI
        # Distutils interface (by Jack Jansen)
        zaimportuj distutils.command
        std_commands = distutils.command.__all__
        is_std = {}
        dla cmd w std_commands:
            is_std[cmd] = 1

        extra_commands = []
        dla cmd w self.cmdclass.keys():
            jeżeli nie is_std.get(cmd):
                extra_commands.append(cmd)

        rv = []
        dla cmd w (std_commands + extra_commands):
            klass = self.cmdclass.get(cmd)
            jeżeli nie klass:
                klass = self.get_command_class(cmd)
            spróbuj:
                description = klass.description
            wyjąwszy AttributeError:
                description = "(no description available)"
            rv.append((cmd, description))
        zwróć rv

    # -- Command class/object methods ----------------------------------

    def get_command_packages(self):
        """Return a list of packages z which commands are loaded."""
        pkgs = self.command_packages
        jeżeli nie isinstance(pkgs, list):
            jeżeli pkgs jest Nic:
                pkgs = ''
            pkgs = [pkg.strip() dla pkg w pkgs.split(',') jeżeli pkg != '']
            jeżeli "distutils.command" nie w pkgs:
                pkgs.insert(0, "distutils.command")
            self.command_packages = pkgs
        zwróć pkgs

    def get_command_class(self, command):
        """Return the klasa that implements the Distutils command named by
        'command'.  First we check the 'cmdclass' dictionary; jeżeli the
        command jest mentioned there, we fetch the klasa object z the
        dictionary oraz zwróć it.  Otherwise we load the command module
        ("distutils.command." + command) oraz fetch the command klasa from
        the module.  The loaded klasa jest also stored w 'cmdclass'
        to speed future calls to 'get_command_class()'.

        Raises DistutilsModuleError jeżeli the expected module could nie be
        found, albo jeżeli that module does nie define the expected class.
        """
        klass = self.cmdclass.get(command)
        jeżeli klass:
            zwróć klass

        dla pkgname w self.get_command_packages():
            module_name = "%s.%s" % (pkgname, command)
            klass_name = command

            spróbuj:
                __import__(module_name)
                module = sys.modules[module_name]
            wyjąwszy ImportError:
                kontynuuj

            spróbuj:
                klass = getattr(module, klass_name)
            wyjąwszy AttributeError:
                podnieś DistutilsModuleError(
                    "invalid command '%s' (no klasa '%s' w module '%s')"
                    % (command, klass_name, module_name))

            self.cmdclass[command] = klass
            zwróć klass

        podnieś DistutilsModuleError("invalid command '%s'" % command)

    def get_command_obj(self, command, create=1):
        """Return the command object dla 'command'.  Normally this object
        jest cached on a previous call to 'get_command_obj()'; jeżeli no command
        object dla 'command' jest w the cache, then we either create oraz
        zwróć it (jeżeli 'create' jest true) albo zwróć Nic.
        """
        cmd_obj = self.command_obj.get(command)
        jeżeli nie cmd_obj oraz create:
            jeżeli DEBUG:
                self.announce("Distribution.get_command_obj(): "
                              "creating '%s' command object" % command)

            klass = self.get_command_class(command)
            cmd_obj = self.command_obj[command] = klass(self)
            self.have_run[command] = 0

            # Set any options that were supplied w config files
            # albo on the command line.  (NB. support dla error
            # reporting jest lame here: any errors aren't reported
            # until 'finalize_options()' jest called, which means
            # we won't report the source of the error.)
            options = self.command_options.get(command)
            jeżeli options:
                self._set_command_options(cmd_obj, options)

        zwróć cmd_obj

    def _set_command_options(self, command_obj, option_dict=Nic):
        """Set the options dla 'command_obj' z 'option_dict'.  Basically
        this means copying elements of a dictionary ('option_dict') to
        attributes of an instance ('command').

        'command_obj' must be a Command instance.  If 'option_dict' jest nie
        supplied, uses the standard option dictionary dla this command
        (z 'self.command_options').
        """
        command_name = command_obj.get_command_name()
        jeżeli option_dict jest Nic:
            option_dict = self.get_option_dict(command_name)

        jeżeli DEBUG:
            self.announce("  setting options dla '%s' command:" % command_name)
        dla (option, (source, value)) w option_dict.items():
            jeżeli DEBUG:
                self.announce("    %s = %s (z %s)" % (option, value,
                                                         source))
            spróbuj:
                bool_opts = [translate_longopt(o)
                             dla o w command_obj.boolean_options]
            wyjąwszy AttributeError:
                bool_opts = []
            spróbuj:
                neg_opt = command_obj.negative_opt
            wyjąwszy AttributeError:
                neg_opt = {}

            spróbuj:
                is_string = isinstance(value, str)
                jeżeli option w neg_opt oraz is_string:
                    setattr(command_obj, neg_opt[option], nie strtobool(value))
                albo_inaczej option w bool_opts oraz is_string:
                    setattr(command_obj, option, strtobool(value))
                albo_inaczej hasattr(command_obj, option):
                    setattr(command_obj, option, value)
                inaczej:
                    podnieś DistutilsOptionError(
                        "error w %s: command '%s' has no such option '%s'"
                        % (source, command_name, option))
            wyjąwszy ValueError jako msg:
                podnieś DistutilsOptionError(msg)

    def reinitialize_command(self, command, reinit_subcommands=0):
        """Reinitializes a command to the state it was w when first
        returned by 'get_command_obj()': ie., initialized but nie yet
        finalized.  This provides the opportunity to sneak option
        values w programmatically, overriding albo supplementing
        user-supplied values z the config files oraz command line.
        You'll have to re-finalize the command object (by calling
        'finalize_options()' albo 'ensure_finalized()') before using it for
        real.

        'command' should be a command name (string) albo command object.  If
        'reinit_subcommands' jest true, also reinitializes the command's
        sub-commands, jako declared by the 'sub_commands' klasa attribute (if
        it has one).  See the "install" command dla an example.  Only
        reinitializes the sub-commands that actually matter, ie. those
        whose test predicates zwróć true.

        Returns the reinitialized command object.
        """
        z distutils.cmd zaimportuj Command
        jeżeli nie isinstance(command, Command):
            command_name = command
            command = self.get_command_obj(command_name)
        inaczej:
            command_name = command.get_command_name()

        jeżeli nie command.finalized:
            zwróć command
        command.initialize_options()
        command.finalized = 0
        self.have_run[command_name] = 0
        self._set_command_options(command)

        jeżeli reinit_subcommands:
            dla sub w command.get_sub_commands():
                self.reinitialize_command(sub, reinit_subcommands)

        zwróć command

    # -- Methods that operate on the Distribution ----------------------

    def announce(self, msg, level=log.INFO):
        log.log(level, msg)

    def run_commands(self):
        """Run each command that was seen on the setup script command line.
        Uses the list of commands found oraz cache of command objects
        created by 'get_command_obj()'.
        """
        dla cmd w self.commands:
            self.run_command(cmd)

    # -- Methods that operate on its Commands --------------------------

    def run_command(self, command):
        """Do whatever it takes to run a command (including nothing at all,
        jeżeli the command has already been run).  Specifically: jeżeli we have
        already created oraz run the command named by 'command', zwróć
        silently without doing anything.  If the command named by 'command'
        doesn't even have a command object yet, create one.  Then invoke
        'run()' on that command object (or an existing one).
        """
        # Already been here, done that? then zwróć silently.
        jeżeli self.have_run.get(command):
            zwróć

        log.info("running %s", command)
        cmd_obj = self.get_command_obj(command)
        cmd_obj.ensure_finalized()
        cmd_obj.run()
        self.have_run[command] = 1

    # -- Distribution query methods ------------------------------------

    def has_pure_modules(self):
        zwróć len(self.packages albo self.py_modules albo []) > 0

    def has_ext_modules(self):
        zwróć self.ext_modules oraz len(self.ext_modules) > 0

    def has_c_libraries(self):
        zwróć self.libraries oraz len(self.libraries) > 0

    def has_modules(self):
        zwróć self.has_pure_modules() albo self.has_ext_modules()

    def has_headers(self):
        zwróć self.headers oraz len(self.headers) > 0

    def has_scripts(self):
        zwróć self.scripts oraz len(self.scripts) > 0

    def has_data_files(self):
        zwróć self.data_files oraz len(self.data_files) > 0

    def is_pure(self):
        zwróć (self.has_pure_modules() oraz
                nie self.has_ext_modules() oraz
                nie self.has_c_libraries())

    # -- Metadata query methods ----------------------------------------

    # If you're looking dla 'get_name()', 'get_version()', oraz so forth,
    # they are defined w a sneaky way: the constructor binds self.get_XXX
    # to self.metadata.get_XXX.  The actual code jest w the
    # DistributionMetadata class, below.

klasa DistributionMetadata:
    """Dummy klasa to hold the distribution meta-data: name, version,
    author, oraz so forth.
    """

    _METHOD_BASENAMES = ("name", "version", "author", "author_email",
                         "maintainer", "maintainer_email", "url",
                         "license", "description", "long_description",
                         "keywords", "platforms", "fullname", "contact",
                         "contact_email", "license", "classifiers",
                         "download_url",
                         # PEP 314
                         "provides", "requires", "obsoletes",
                         )

    def __init__(self, path=Nic):
        jeżeli path jest nie Nic:
            self.read_pkg_file(open(path))
        inaczej:
            self.name = Nic
            self.version = Nic
            self.author = Nic
            self.author_email = Nic
            self.maintainer = Nic
            self.maintainer_email = Nic
            self.url = Nic
            self.license = Nic
            self.description = Nic
            self.long_description = Nic
            self.keywords = Nic
            self.platforms = Nic
            self.classifiers = Nic
            self.download_url = Nic
            # PEP 314
            self.provides = Nic
            self.requires = Nic
            self.obsoletes = Nic

    def read_pkg_file(self, file):
        """Reads the metadata values z a file object."""
        msg = message_from_file(file)

        def _read_field(name):
            value = msg[name]
            jeżeli value == 'UNKNOWN':
                zwróć Nic
            zwróć value

        def _read_list(name):
            values = msg.get_all(name, Nic)
            jeżeli values == []:
                zwróć Nic
            zwróć values

        metadata_version = msg['metadata-version']
        self.name = _read_field('name')
        self.version = _read_field('version')
        self.description = _read_field('summary')
        # we are filling author only.
        self.author = _read_field('author')
        self.maintainer = Nic
        self.author_email = _read_field('author-email')
        self.maintainer_email = Nic
        self.url = _read_field('home-page')
        self.license = _read_field('license')

        jeżeli 'download-url' w msg:
            self.download_url = _read_field('download-url')
        inaczej:
            self.download_url = Nic

        self.long_description = _read_field('description')
        self.description = _read_field('summary')

        jeżeli 'keywords' w msg:
            self.keywords = _read_field('keywords').split(',')

        self.platforms = _read_list('platform')
        self.classifiers = _read_list('classifier')

        # PEP 314 - these fields only exist w 1.1
        jeżeli metadata_version == '1.1':
            self.requires = _read_list('requires')
            self.provides = _read_list('provides')
            self.obsoletes = _read_list('obsoletes')
        inaczej:
            self.requires = Nic
            self.provides = Nic
            self.obsoletes = Nic

    def write_pkg_info(self, base_dir):
        """Write the PKG-INFO file into the release tree.
        """
        przy open(os.path.join(base_dir, 'PKG-INFO'), 'w',
                  encoding='UTF-8') jako pkg_info:
            self.write_pkg_file(pkg_info)

    def write_pkg_file(self, file):
        """Write the PKG-INFO format data to a file object.
        """
        version = '1.0'
        jeżeli (self.provides albo self.requires albo self.obsoletes albo
                self.classifiers albo self.download_url):
            version = '1.1'

        file.write('Metadata-Version: %s\n' % version)
        file.write('Name: %s\n' % self.get_name())
        file.write('Version: %s\n' % self.get_version())
        file.write('Summary: %s\n' % self.get_description())
        file.write('Home-page: %s\n' % self.get_url())
        file.write('Author: %s\n' % self.get_contact())
        file.write('Author-email: %s\n' % self.get_contact_email())
        file.write('License: %s\n' % self.get_license())
        jeżeli self.download_url:
            file.write('Download-URL: %s\n' % self.download_url)

        long_desc = rfc822_escape(self.get_long_description())
        file.write('Description: %s\n' % long_desc)

        keywords = ','.join(self.get_keywords())
        jeżeli keywords:
            file.write('Keywords: %s\n' % keywords)

        self._write_list(file, 'Platform', self.get_platforms())
        self._write_list(file, 'Classifier', self.get_classifiers())

        # PEP 314
        self._write_list(file, 'Requires', self.get_requires())
        self._write_list(file, 'Provides', self.get_provides())
        self._write_list(file, 'Obsoletes', self.get_obsoletes())

    def _write_list(self, file, name, values):
        dla value w values:
            file.write('%s: %s\n' % (name, value))

    # -- Metadata query methods ----------------------------------------

    def get_name(self):
        zwróć self.name albo "UNKNOWN"

    def get_version(self):
        zwróć self.version albo "0.0.0"

    def get_fullname(self):
        zwróć "%s-%s" % (self.get_name(), self.get_version())

    def get_author(self):
        zwróć self.author albo "UNKNOWN"

    def get_author_email(self):
        zwróć self.author_email albo "UNKNOWN"

    def get_maintainer(self):
        zwróć self.maintainer albo "UNKNOWN"

    def get_maintainer_email(self):
        zwróć self.maintainer_email albo "UNKNOWN"

    def get_contact(self):
        zwróć self.maintainer albo self.author albo "UNKNOWN"

    def get_contact_email(self):
        zwróć self.maintainer_email albo self.author_email albo "UNKNOWN"

    def get_url(self):
        zwróć self.url albo "UNKNOWN"

    def get_license(self):
        zwróć self.license albo "UNKNOWN"
    get_licence = get_license

    def get_description(self):
        zwróć self.description albo "UNKNOWN"

    def get_long_description(self):
        zwróć self.long_description albo "UNKNOWN"

    def get_keywords(self):
        zwróć self.keywords albo []

    def get_platforms(self):
        zwróć self.platforms albo ["UNKNOWN"]

    def get_classifiers(self):
        zwróć self.classifiers albo []

    def get_download_url(self):
        zwróć self.download_url albo "UNKNOWN"

    # PEP 314
    def get_requires(self):
        zwróć self.requires albo []

    def set_requires(self, value):
        zaimportuj distutils.versionpredicate
        dla v w value:
            distutils.versionpredicate.VersionPredicate(v)
        self.requires = value

    def get_provides(self):
        zwróć self.provides albo []

    def set_provides(self, value):
        value = [v.strip() dla v w value]
        dla v w value:
            zaimportuj distutils.versionpredicate
            distutils.versionpredicate.split_provision(v)
        self.provides = value

    def get_obsoletes(self):
        zwróć self.obsoletes albo []

    def set_obsoletes(self, value):
        zaimportuj distutils.versionpredicate
        dla v w value:
            distutils.versionpredicate.VersionPredicate(v)
        self.obsoletes = value

def fix_help_options(options):
    """Convert a 4-tuple 'help_options' list jako found w various command
    classes to the 3-tuple form required by FancyGetopt.
    """
    new_options = []
    dla help_tuple w options:
        new_options.append(help_tuple[0:3])
    zwróć new_options
