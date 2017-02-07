"""distutils.cmd

Provides the Command class, the base klasa dla the command classes
in the distutils.command package.
"""

zaimportuj sys, os, re
z distutils.errors zaimportuj DistutilsOptionError
z distutils zaimportuj util, dir_util, file_util, archive_util, dep_util
z distutils zaimportuj log

klasa Command:
    """Abstract base klasa dla defining command classes, the "worker bees"
    of the Distutils.  A useful analogy dla command classes jest to think of
    them jako subroutines przy local variables called "options".  The options
    are "declared" w 'initialize_options()' oraz "defined" (given their
    final values, aka "finalized") w 'finalize_options()', both of which
    must be defined by every command class.  The distinction between the
    two jest necessary because option values might come z the outside
    world (command line, config file, ...), oraz any options dependent on
    other options must be computed *after* these outside influences have
    been processed -- hence 'finalize_options()'.  The "body" of the
    subroutine, where it does all its work based on the values of its
    options, jest the 'run()' method, which must also be implemented by every
    command class.
    """

    # 'sub_commands' formalizes the notion of a "family" of commands,
    # eg. "install" jako the parent przy sub-commands "install_lib",
    # "install_headers", etc.  The parent of a family of commands
    # defines 'sub_commands' jako a klasa attribute; it's a list of
    #    (command_name : string, predicate : unbound_method | string | Nic)
    # tuples, where 'predicate' jest a method of the parent command that
    # determines whether the corresponding command jest applicable w the
    # current situation.  (Eg. we "install_headers" jest only applicable if
    # we have any C header files to install.)  If 'predicate' jest Nic,
    # that command jest always applicable.
    #
    # 'sub_commands' jest usually defined at the *end* of a class, because
    # predicates can be unbound methods, so they must already have been
    # defined.  The canonical example jest the "install" command.
    sub_commands = []


    # -- Creation/initialization methods -------------------------------

    def __init__(self, dist):
        """Create oraz initialize a new Command object.  Most importantly,
        invokes the 'initialize_options()' method, which jest the real
        initializer oraz depends on the actual command being
        instantiated.
        """
        # late zaimportuj because of mutual dependence between these classes
        z distutils.dist zaimportuj Distribution

        jeżeli nie isinstance(dist, Distribution):
            podnieś TypeError("dist must be a Distribution instance")
        jeżeli self.__class__ jest Command:
            podnieś RuntimeError("Command jest an abstract class")

        self.distribution = dist
        self.initialize_options()

        # Per-command versions of the global flags, so that the user can
        # customize Distutils' behaviour command-by-command oraz let some
        # commands fall back on the Distribution's behaviour.  Nic means
        # "not defined, check self.distribution's copy", dopóki 0 albo 1 mean
        # false oraz true (duh).  Note that this means figuring out the real
        # value of each flag jest a touch complicated -- hence "self._dry_run"
        # will be handled by __getattr__, below.
        # XXX This needs to be fixed.
        self._dry_run = Nic

        # verbose jest largely ignored, but needs to be set for
        # backwards compatibility (I think)?
        self.verbose = dist.verbose

        # Some commands define a 'self.force' option to ignore file
        # timestamps, but methods defined *here* assume that
        # 'self.force' exists dla all commands.  So define it here
        # just to be safe.
        self.force = Nic

        # The 'help' flag jest just used dla command-line parsing, so
        # none of that complicated bureaucracy jest needed.
        self.help = 0

        # 'finalized' records whether albo nie 'finalize_options()' has been
        # called.  'finalize_options()' itself should nie pay attention to
        # this flag: it jest the business of 'ensure_finalized()', which
        # always calls 'finalize_options()', to respect/update it.
        self.finalized = 0

    # XXX A more explicit way to customize dry_run would be better.
    def __getattr__(self, attr):
        jeżeli attr == 'dry_run':
            myval = getattr(self, "_" + attr)
            jeżeli myval jest Nic:
                zwróć getattr(self.distribution, attr)
            inaczej:
                zwróć myval
        inaczej:
            podnieś AttributeError(attr)

    def ensure_finalized(self):
        jeżeli nie self.finalized:
            self.finalize_options()
        self.finalized = 1

    # Subclasses must define:
    #   initialize_options()
    #     provide default values dla all options; may be customized by
    #     setup script, by options z config file(s), albo by command-line
    #     options
    #   finalize_options()
    #     decide on the final values dla all options; this jest called
    #     after all possible intervention z the outside world
    #     (command-line, option file, etc.) has been processed
    #   run()
    #     run the command: do whatever it jest we're here to do,
    #     controlled by the command's various option values

    def initialize_options(self):
        """Set default values dla all the options that this command
        supports.  Note that these defaults may be overridden by other
        commands, by the setup script, by config files, albo by the
        command-line.  Thus, this jest nie the place to code dependencies
        between options; generally, 'initialize_options()' implementations
        are just a bunch of "self.foo = Nic" assignments.

        This method must be implemented by all command classes.
        """
        podnieś RuntimeError("abstract method -- subclass %s must override"
                           % self.__class__)

    def finalize_options(self):
        """Set final values dla all the options that this command supports.
        This jest always called jako late jako possible, ie.  after any option
        assignments z the command-line albo z other commands have been
        done.  Thus, this jest the place to code option dependencies: if
        'foo' depends on 'bar', then it jest safe to set 'foo' z 'bar' as
        long jako 'foo' still has the same value it was assigned w
        'initialize_options()'.

        This method must be implemented by all command classes.
        """
        podnieś RuntimeError("abstract method -- subclass %s must override"
                           % self.__class__)


    def dump_options(self, header=Nic, indent=""):
        z distutils.fancy_getopt zaimportuj longopt_xlate
        jeżeli header jest Nic:
            header = "command options dla '%s':" % self.get_command_name()
        self.announce(indent + header, level=log.INFO)
        indent = indent + "  "
        dla (option, _, _) w self.user_options:
            option = option.translate(longopt_xlate)
            jeżeli option[-1] == "=":
                option = option[:-1]
            value = getattr(self, option)
            self.announce(indent + "%s = %s" % (option, value),
                          level=log.INFO)

    def run(self):
        """A command's raison d'etre: carry out the action it exists to
        perform, controlled by the options initialized w
        'initialize_options()', customized by other commands, the setup
        script, the command-line, oraz config files, oraz finalized w
        'finalize_options()'.  All terminal output oraz filesystem
        interaction should be done by 'run()'.

        This method must be implemented by all command classes.
        """
        podnieś RuntimeError("abstract method -- subclass %s must override"
                           % self.__class__)

    def announce(self, msg, level=1):
        """If the current verbosity level jest of greater than albo equal to
        'level' print 'msg' to stdout.
        """
        log.log(level, msg)

    def debug_print(self, msg):
        """Print 'msg' to stdout jeżeli the global DEBUG (taken z the
        DISTUTILS_DEBUG environment variable) flag jest true.
        """
        z distutils.debug zaimportuj DEBUG
        jeżeli DEBUG:
            print(msg)
            sys.stdout.flush()


    # -- Option validation methods -------------------------------------
    # (these are very handy w writing the 'finalize_options()' method)
    #
    # NB. the general philosophy here jest to ensure that a particular option
    # value meets certain type oraz value constraints.  If not, we try to
    # force it into conformance (eg. jeżeli we expect a list but have a string,
    # split the string on comma and/or whitespace).  If we can't force the
    # option into conformance, podnieś DistutilsOptionError.  Thus, command
    # classes need do nothing more than (eg.)
    #   self.ensure_string_list('foo')
    # oraz they can be guaranteed that thereafter, self.foo will be
    # a list of strings.

    def _ensure_stringlike(self, option, what, default=Nic):
        val = getattr(self, option)
        jeżeli val jest Nic:
            setattr(self, option, default)
            zwróć default
        albo_inaczej nie isinstance(val, str):
            podnieś DistutilsOptionError("'%s' must be a %s (got `%s`)"
                                       % (option, what, val))
        zwróć val

    def ensure_string(self, option, default=Nic):
        """Ensure that 'option' jest a string; jeżeli nie defined, set it to
        'default'.
        """
        self._ensure_stringlike(option, "string", default)

    def ensure_string_list(self, option):
        """Ensure that 'option' jest a list of strings.  If 'option' jest
        currently a string, we split it either on /,\s*/ albo /\s+/, so
        "foo bar baz", "foo,bar,baz", oraz "foo,   bar baz" all become
        ["foo", "bar", "baz"].
        """
        val = getattr(self, option)
        jeżeli val jest Nic:
            zwróć
        albo_inaczej isinstance(val, str):
            setattr(self, option, re.split(r',\s*|\s+', val))
        inaczej:
            jeżeli isinstance(val, list):
                ok = all(isinstance(v, str) dla v w val)
            inaczej:
                ok = Nieprawda
            jeżeli nie ok:
                podnieś DistutilsOptionError(
                      "'%s' must be a list of strings (got %r)"
                      % (option, val))

    def _ensure_tested_string(self, option, tester, what, error_fmt,
                              default=Nic):
        val = self._ensure_stringlike(option, what, default)
        jeżeli val jest nie Nic oraz nie tester(val):
            podnieś DistutilsOptionError(("error w '%s' option: " + error_fmt)
                                       % (option, val))

    def ensure_filename(self, option):
        """Ensure that 'option' jest the name of an existing file."""
        self._ensure_tested_string(option, os.path.isfile,
                                   "filename",
                                   "'%s' does nie exist albo jest nie a file")

    def ensure_dirname(self, option):
        self._ensure_tested_string(option, os.path.isdir,
                                   "directory name",
                                   "'%s' does nie exist albo jest nie a directory")


    # -- Convenience methods dla commands ------------------------------

    def get_command_name(self):
        jeżeli hasattr(self, 'command_name'):
            zwróć self.command_name
        inaczej:
            zwróć self.__class__.__name__

    def set_undefined_options(self, src_cmd, *option_pairs):
        """Set the values of any "undefined" options z corresponding
        option values w some other command object.  "Undefined" here means
        "is Nic", which jest the convention used to indicate that an option
        has nie been changed between 'initialize_options()' oraz
        'finalize_options()'.  Usually called z 'finalize_options()' for
        options that depend on some other command rather than another
        option of the same command.  'src_cmd' jest the other command from
        which option values will be taken (a command object will be created
        dla it jeżeli necessary); the remaining arguments are
        '(src_option,dst_option)' tuples which mean "take the value of
        'src_option' w the 'src_cmd' command object, oraz copy it to
        'dst_option' w the current command object".
        """
        # Option_pairs: list of (src_option, dst_option) tuples
        src_cmd_obj = self.distribution.get_command_obj(src_cmd)
        src_cmd_obj.ensure_finalized()
        dla (src_option, dst_option) w option_pairs:
            jeżeli getattr(self, dst_option) jest Nic:
                setattr(self, dst_option, getattr(src_cmd_obj, src_option))

    def get_finalized_command(self, command, create=1):
        """Wrapper around Distribution's 'get_command_obj()' method: find
        (create jeżeli necessary oraz 'create' jest true) the command object for
        'command', call its 'ensure_finalized()' method, oraz zwróć the
        finalized command object.
        """
        cmd_obj = self.distribution.get_command_obj(command, create)
        cmd_obj.ensure_finalized()
        zwróć cmd_obj

    # XXX rename to 'get_reinitialized_command()'? (should do the
    # same w dist.py, jeżeli so)
    def reinitialize_command(self, command, reinit_subcommands=0):
        zwróć self.distribution.reinitialize_command(command,
                                                      reinit_subcommands)

    def run_command(self, command):
        """Run some other command: uses the 'run_command()' method of
        Distribution, which creates oraz finalizes the command object if
        necessary oraz then invokes its 'run()' method.
        """
        self.distribution.run_command(command)

    def get_sub_commands(self):
        """Determine the sub-commands that are relevant w the current
        distribution (ie., that need to be run).  This jest based on the
        'sub_commands' klasa attribute: each tuple w that list may include
        a method that we call to determine jeżeli the subcommand needs to be
        run dla the current distribution.  Return a list of command names.
        """
        commands = []
        dla (cmd_name, method) w self.sub_commands:
            jeżeli method jest Nic albo method(self):
                commands.append(cmd_name)
        zwróć commands


    # -- External world manipulation -----------------------------------

    def warn(self, msg):
        log.warn("warning: %s: %s\n" %
                (self.get_command_name(), msg))

    def execute(self, func, args, msg=Nic, level=1):
        util.execute(func, args, msg, dry_run=self.dry_run)

    def mkpath(self, name, mode=0o777):
        dir_util.mkpath(name, mode, dry_run=self.dry_run)

    def copy_file(self, infile, outfile, preserve_mode=1, preserve_times=1,
                  link=Nic, level=1):
        """Copy a file respecting verbose, dry-run oraz force flags.  (The
        former two default to whatever jest w the Distribution object, oraz
        the latter defaults to false dla commands that don't define it.)"""
        zwróć file_util.copy_file(infile, outfile, preserve_mode,
                                   preserve_times, nie self.force, link,
                                   dry_run=self.dry_run)

    def copy_tree(self, infile, outfile, preserve_mode=1, preserve_times=1,
                   preserve_symlinks=0, level=1):
        """Copy an entire directory tree respecting verbose, dry-run,
        oraz force flags.
        """
        zwróć dir_util.copy_tree(infile, outfile, preserve_mode,
                                  preserve_times, preserve_symlinks,
                                  nie self.force, dry_run=self.dry_run)

    def move_file (self, src, dst, level=1):
        """Move a file respecting dry-run flag."""
        zwróć file_util.move_file(src, dst, dry_run=self.dry_run)

    def spawn(self, cmd, search_path=1, level=1):
        """Spawn an external command respecting dry-run flag."""
        z distutils.spawn zaimportuj spawn
        spawn(cmd, search_path, dry_run=self.dry_run)

    def make_archive(self, base_name, format, root_dir=Nic, base_dir=Nic,
                     owner=Nic, group=Nic):
        zwróć archive_util.make_archive(base_name, format, root_dir, base_dir,
                                         dry_run=self.dry_run,
                                         owner=owner, group=group)

    def make_file(self, infiles, outfile, func, args,
                  exec_msg=Nic, skip_msg=Nic, level=1):
        """Special case of 'execute()' dla operations that process one albo
        more input files oraz generate one output file.  Works just like
        'execute()', wyjąwszy the operation jest skipped oraz a different
        message printed jeżeli 'outfile' already exists oraz jest newer than all
        files listed w 'infiles'.  If the command defined 'self.force',
        oraz it jest true, then the command jest unconditionally run -- does no
        timestamp checks.
        """
        jeżeli skip_msg jest Nic:
            skip_msg = "skipping %s (inputs unchanged)" % outfile

        # Allow 'infiles' to be a single string
        jeżeli isinstance(infiles, str):
            infiles = (infiles,)
        albo_inaczej nie isinstance(infiles, (list, tuple)):
            podnieś TypeError(
                  "'infiles' must be a string, albo a list albo tuple of strings")

        jeżeli exec_msg jest Nic:
            exec_msg = "generating %s z %s" % (outfile, ', '.join(infiles))

        # If 'outfile' must be regenerated (either because it doesn't
        # exist, jest out-of-date, albo the 'force' flag jest true) then
        # perform the action that presumably regenerates it
        jeżeli self.force albo dep_util.newer_group(infiles, outfile):
            self.execute(func, args, exec_msg, level)
        # Otherwise, print the "skip" message
        inaczej:
            log.debug(skip_msg)

# XXX 'install_misc' klasa nie currently used -- it was the base klasa for
# both 'install_scripts' oraz 'install_data', but they outgrew it.  It might
# still be useful dla 'install_headers', though, so I'm keeping it around
# dla the time being.

klasa install_misc(Command):
    """Common base klasa dla installing some files w a subdirectory.
    Currently used by install_data oraz install_scripts.
    """

    user_options = [('install-dir=', 'd', "directory to install the files to")]

    def initialize_options (self):
        self.install_dir = Nic
        self.outfiles = []

    def _install_dir_from(self, dirname):
        self.set_undefined_options('install', (dirname, 'install_dir'))

    def _copy_files(self, filelist):
        self.outfiles = []
        jeżeli nie filelist:
            zwróć
        self.mkpath(self.install_dir)
        dla f w filelist:
            self.copy_file(f, self.install_dir)
            self.outfiles.append(os.path.join(self.install_dir, f))

    def get_outputs(self):
        zwróć self.outfiles
