"""distutils.core

The only module that needs to be imported to use the Distutils; provides
the 'setup' function (which jest to be called z the setup script).  Also
indirectly provides the Distribution oraz Command classes, although they are
really defined w distutils.dist oraz distutils.cmd.
"""

zaimportuj os
zaimportuj sys

z distutils.debug zaimportuj DEBUG
z distutils.errors zaimportuj *

# Mainly zaimportuj these so setup scripts can "z distutils.core import" them.
z distutils.dist zaimportuj Distribution
z distutils.cmd zaimportuj Command
z distutils.config zaimportuj PyPIRCCommand
z distutils.extension zaimportuj Extension

# This jest a barebones help message generated displayed when the user
# runs the setup script przy no arguments at all.  More useful help
# jest generated przy various --help options: global help, list commands,
# oraz per-command help.
USAGE = """\
usage: %(script)s [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
   or: %(script)s --help [cmd1 cmd2 ...]
   or: %(script)s --help-commands
   or: %(script)s cmd --help
"""

def gen_usage (script_name):
    script = os.path.basename(script_name)
    zwróć USAGE % vars()


# Some mild magic to control the behaviour of 'setup()' z 'run_setup()'.
_setup_stop_after = Nic
_setup_distribution = Nic

# Legal keyword arguments dla the setup() function
setup_keywords = ('distclass', 'script_name', 'script_args', 'options',
                  'name', 'version', 'author', 'author_email',
                  'maintainer', 'maintainer_email', 'url', 'license',
                  'description', 'long_description', 'keywords',
                  'platforms', 'classifiers', 'download_url',
                  'requires', 'provides', 'obsoletes',
                  )

# Legal keyword arguments dla the Extension constructor
extension_keywords = ('name', 'sources', 'include_dirs',
                      'define_macros', 'undef_macros',
                      'library_dirs', 'libraries', 'runtime_library_dirs',
                      'extra_objects', 'extra_compile_args', 'extra_link_args',
                      'swig_opts', 'export_symbols', 'depends', 'language')

def setup (**attrs):
    """The gateway to the Distutils: do everything your setup script needs
    to do, w a highly flexible oraz user-driven way.  Briefly: create a
    Distribution instance; find oraz parse config files; parse the command
    line; run each Distutils command found there, customized by the options
    supplied to 'setup()' (as keyword arguments), w config files, oraz on
    the command line.

    The Distribution instance might be an instance of a klasa supplied via
    the 'distclass' keyword argument to 'setup'; jeżeli no such klasa jest
    supplied, then the Distribution klasa (in dist.py) jest instantiated.
    All other arguments to 'setup' (wyjąwszy dla 'cmdclass') are used to set
    attributes of the Distribution instance.

    The 'cmdclass' argument, jeżeli supplied, jest a dictionary mapping command
    names to command classes.  Each command encountered on the command line
    will be turned into a command class, which jest w turn instantiated; any
    klasa found w 'cmdclass' jest used w place of the default, which jest
    (dla command 'foo_bar') klasa 'foo_bar' w module
    'distutils.command.foo_bar'.  The command klasa must provide a
    'user_options' attribute which jest a list of option specifiers for
    'distutils.fancy_getopt'.  Any command-line options between the current
    oraz the next command are used to set attributes of the current command
    object.

    When the entire command-line has been successfully parsed, calls the
    'run()' method on each command object w turn.  This method will be
    driven entirely by the Distribution object (which each command object
    has a reference to, thanks to its constructor), oraz the
    command-specific options that became attributes of each command
    object.
    """

    global _setup_stop_after, _setup_distribution

    # Determine the distribution klasa -- either caller-supplied albo
    # our Distribution (see below).
    klass = attrs.get('distclass')
    jeżeli klass:
        usuń attrs['distclass']
    inaczej:
        klass = Distribution

    jeżeli 'script_name' nie w attrs:
        attrs['script_name'] = os.path.basename(sys.argv[0])
    jeżeli 'script_args'  nie w attrs:
        attrs['script_args'] = sys.argv[1:]

    # Create the Distribution instance, using the remaining arguments
    # (ie. everything wyjąwszy distclass) to initialize it
    spróbuj:
        _setup_distribution = dist = klass(attrs)
    wyjąwszy DistutilsSetupError jako msg:
        jeżeli 'name' nie w attrs:
            podnieś SystemExit("error w setup command: %s" % msg)
        inaczej:
            podnieś SystemExit("error w %s setup command: %s" % \
                  (attrs['name'], msg))

    jeżeli _setup_stop_after == "init":
        zwróć dist

    # Find oraz parse the config file(s): they will override options from
    # the setup script, but be overridden by the command line.
    dist.parse_config_files()

    jeżeli DEBUG:
        print("options (after parsing config files):")
        dist.dump_option_dicts()

    jeżeli _setup_stop_after == "config":
        zwróć dist

    # Parse the command line oraz override config files; any
    # command-line errors are the end user's fault, so turn them into
    # SystemExit to suppress tracebacks.
    spróbuj:
        ok = dist.parse_command_line()
    wyjąwszy DistutilsArgError jako msg:
        podnieś SystemExit(gen_usage(dist.script_name) + "\nerror: %s" % msg)

    jeżeli DEBUG:
        print("options (after parsing command line):")
        dist.dump_option_dicts()

    jeżeli _setup_stop_after == "commandline":
        zwróć dist

    # And finally, run all the commands found on the command line.
    jeżeli ok:
        spróbuj:
            dist.run_commands()
        wyjąwszy KeyboardInterrupt:
            podnieś SystemExit("interrupted")
        wyjąwszy OSError jako exc:
            jeżeli DEBUG:
                sys.stderr.write("error: %s\n" % (exc,))
                podnieś
            inaczej:
                podnieś SystemExit("error: %s" % (exc,))

        wyjąwszy (DistutilsError,
                CCompilerError) jako msg:
            jeżeli DEBUG:
                podnieś
            inaczej:
                podnieś SystemExit("error: " + str(msg))

    zwróć dist

# setup ()


def run_setup (script_name, script_args=Nic, stop_after="run"):
    """Run a setup script w a somewhat controlled environment, oraz
    zwróć the Distribution instance that drives things.  This jest useful
    jeżeli you need to find out the distribution meta-data (passed as
    keyword args z 'script' to 'setup()', albo the contents of the
    config files albo command-line.

    'script_name' jest a file that will be read oraz run przy 'exec()';
    'sys.argv[0]' will be replaced przy 'script' dla the duration of the
    call.  'script_args' jest a list of strings; jeżeli supplied,
    'sys.argv[1:]' will be replaced by 'script_args' dla the duration of
    the call.

    'stop_after' tells 'setup()' when to stop processing; possible
    values:
      init
        stop after the Distribution instance has been created oraz
        populated przy the keyword arguments to 'setup()'
      config
        stop after config files have been parsed (and their data
        stored w the Distribution instance)
      commandline
        stop after the command-line ('sys.argv[1:]' albo 'script_args')
        have been parsed (and the data stored w the Distribution)
      run [default]
        stop after all commands have been run (the same jako jeżeli 'setup()'
        had been called w the usual way

    Returns the Distribution instance, which provides all information
    used to drive the Distutils.
    """
    jeżeli stop_after nie w ('init', 'config', 'commandline', 'run'):
        podnieś ValueError("invalid value dla 'stop_after': %r" % (stop_after,))

    global _setup_stop_after, _setup_distribution
    _setup_stop_after = stop_after

    save_argv = sys.argv
    g = {'__file__': script_name}
    l = {}
    spróbuj:
        spróbuj:
            sys.argv[0] = script_name
            jeżeli script_args jest nie Nic:
                sys.argv[1:] = script_args
            przy open(script_name, 'rb') jako f:
                exec(f.read(), g, l)
        w_końcu:
            sys.argv = save_argv
            _setup_stop_after = Nic
    wyjąwszy SystemExit:
        # Hmm, should we do something jeżeli exiting przy a non-zero code
        # (ie. error)?
        dalej

    jeżeli _setup_distribution jest Nic:
        podnieś RuntimeError(("'distutils.core.setup()' was never called -- "
               "perhaps '%s' jest nie a Distutils setup script?") % \
              script_name)

    # I wonder jeżeli the setup script's namespace -- g oraz l -- would be of
    # any interest to callers?
    #print "_setup_distribution:", _setup_distribution
    zwróć _setup_distribution

# run_setup ()
