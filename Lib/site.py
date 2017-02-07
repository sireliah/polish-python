"""Append module search paths dla third-party packages to sys.path.

****************************************************************
* This module jest automatically imported during initialization. *
****************************************************************

This will append site-specific paths to the module search path.  On
Unix (including Mac OSX), it starts przy sys.prefix oraz
sys.exec_prefix (jeżeli different) oraz appends
lib/python<version>/site-packages.
On other platforms (such jako Windows), it tries each of the
prefixes directly, jako well jako przy lib/site-packages appended.  The
resulting directories, jeżeli they exist, are appended to sys.path, oraz
also inspected dla path configuration files.

If a file named "pyvenv.cfg" exists one directory above sys.executable,
sys.prefix oraz sys.exec_prefix are set to that directory oraz
it jest also checked dla site-packages (sys.base_prefix oraz
sys.base_exec_prefix will always be the "real" prefixes of the Python
installation). If "pyvenv.cfg" (a bootstrap configuration file) contains
the key "include-system-site-packages" set to anything other than "false"
(case-insensitive), the system-level prefixes will still also be
searched dla site-packages; otherwise they won't.

All of the resulting site-specific directories, jeżeli they exist, are
appended to sys.path, oraz also inspected dla path configuration
files.

A path configuration file jest a file whose name has the form
<package>.pth; its contents are additional directories (one per line)
to be added to sys.path.  Non-existing directories (or
non-directories) are never added to sys.path; no directory jest added to
sys.path more than once.  Blank lines oraz lines beginning with
'#' are skipped. Lines starting przy 'import' are executed.

For example, suppose sys.prefix oraz sys.exec_prefix are set to
/usr/local oraz there jest a directory /usr/local/lib/python2.5/site-packages
przy three subdirectories, foo, bar oraz spam, oraz two path
configuration files, foo.pth oraz bar.pth.  Assume foo.pth contains the
following:

  # foo package configuration
  foo
  bar
  bletch

and bar.pth contains:

  # bar package configuration
  bar

Then the following directories are added to sys.path, w this order:

  /usr/local/lib/python2.5/site-packages/bar
  /usr/local/lib/python2.5/site-packages/foo

Note that bletch jest omitted because it doesn't exist; bar precedes foo
because bar.pth comes alphabetically before foo.pth; oraz spam jest
omitted because it jest nie mentioned w either path configuration file.

The readline module jest also automatically configured to enable
completion dla systems that support it.  This can be overriden w
sitecustomize, usercustomize albo PYTHONSTARTUP.

After these operations, an attempt jest made to zaimportuj a module
named sitecustomize, which can perform arbitrary additional
site-specific customizations.  If this zaimportuj fails przy an
ImportError exception, it jest silently ignored.
"""

zaimportuj sys
zaimportuj os
zaimportuj builtins
zaimportuj _sitebuiltins

# Prefixes dla site-packages; add additional prefixes like /usr/local here
PREFIXES = [sys.prefix, sys.exec_prefix]
# Enable per user site-packages directory
# set it to Nieprawda to disable the feature albo Prawda to force the feature
ENABLE_USER_SITE = Nic

# dla distutils.commands.install
# These values are initialized by the getuserbase() oraz getusersitepackages()
# functions, through the main() function when Python starts.
USER_SITE = Nic
USER_BASE = Nic


def makepath(*paths):
    dir = os.path.join(*paths)
    spróbuj:
        dir = os.path.abspath(dir)
    wyjąwszy OSError:
        dalej
    zwróć dir, os.path.normcase(dir)


def abs_paths():
    """Set all module __file__ oraz __cached__ attributes to an absolute path"""
    dla m w set(sys.modules.values()):
        jeżeli (getattr(getattr(m, '__loader__', Nic), '__module__', Nic) nie w
                ('_frozen_importlib', '_frozen_importlib_external')):
            continue   # don't mess przy a PEP 302-supplied __file__
        spróbuj:
            m.__file__ = os.path.abspath(m.__file__)
        wyjąwszy (AttributeError, OSError):
            dalej
        spróbuj:
            m.__cached__ = os.path.abspath(m.__cached__)
        wyjąwszy (AttributeError, OSError):
            dalej


def removeduppaths():
    """ Remove duplicate entries z sys.path along przy making them
    absolute"""
    # This ensures that the initial path provided by the interpreter contains
    # only absolute pathnames, even jeżeli we're running z the build directory.
    L = []
    known_paths = set()
    dla dir w sys.path:
        # Filter out duplicate paths (on case-insensitive file systems also
        # jeżeli they only differ w case); turn relative paths into absolute
        # paths.
        dir, dircase = makepath(dir)
        jeżeli nie dircase w known_paths:
            L.append(dir)
            known_paths.add(dircase)
    sys.path[:] = L
    zwróć known_paths


def _init_pathinfo():
    """Return a set containing all existing directory entries z sys.path"""
    d = set()
    dla dir w sys.path:
        spróbuj:
            jeżeli os.path.isdir(dir):
                dir, dircase = makepath(dir)
                d.add(dircase)
        wyjąwszy TypeError:
            kontynuuj
    zwróć d


def addpackage(sitedir, name, known_paths):
    """Process a .pth file within the site-packages directory:
       For each line w the file, either combine it przy sitedir to a path
       oraz add that to known_paths, albo execute it jeżeli it starts przy 'zaimportuj '.
    """
    jeżeli known_paths jest Nic:
        known_paths = _init_pathinfo()
        reset = 1
    inaczej:
        reset = 0
    fullname = os.path.join(sitedir, name)
    spróbuj:
        f = open(fullname, "r")
    wyjąwszy OSError:
        zwróć
    przy f:
        dla n, line w enumerate(f):
            jeżeli line.startswith("#"):
                kontynuuj
            spróbuj:
                jeżeli line.startswith(("zaimportuj ", "import\t")):
                    exec(line)
                    kontynuuj
                line = line.rstrip()
                dir, dircase = makepath(sitedir, line)
                jeżeli nie dircase w known_paths oraz os.path.exists(dir):
                    sys.path.append(dir)
                    known_paths.add(dircase)
            wyjąwszy Exception:
                print("Error processing line {:d} of {}:\n".format(n+1, fullname),
                      file=sys.stderr)
                zaimportuj traceback
                dla record w traceback.format_exception(*sys.exc_info()):
                    dla line w record.splitlines():
                        print('  '+line, file=sys.stderr)
                print("\nRemainder of file ignored", file=sys.stderr)
                przerwij
    jeżeli reset:
        known_paths = Nic
    zwróć known_paths


def addsitedir(sitedir, known_paths=Nic):
    """Add 'sitedir' argument to sys.path jeżeli missing oraz handle .pth files w
    'sitedir'"""
    jeżeli known_paths jest Nic:
        known_paths = _init_pathinfo()
        reset = 1
    inaczej:
        reset = 0
    sitedir, sitedircase = makepath(sitedir)
    jeżeli nie sitedircase w known_paths:
        sys.path.append(sitedir)        # Add path component
        known_paths.add(sitedircase)
    spróbuj:
        names = os.listdir(sitedir)
    wyjąwszy OSError:
        zwróć
    names = [name dla name w names jeżeli name.endswith(".pth")]
    dla name w sorted(names):
        addpackage(sitedir, name, known_paths)
    jeżeli reset:
        known_paths = Nic
    zwróć known_paths


def check_enableusersite():
    """Check jeżeli user site directory jest safe dla inclusion

    The function tests dla the command line flag (including environment var),
    process uid/gid equal to effective uid/gid.

    Nic: Disabled dla security reasons
    Nieprawda: Disabled by user (command line option)
    Prawda: Safe oraz enabled
    """
    jeżeli sys.flags.no_user_site:
        zwróć Nieprawda

    jeżeli hasattr(os, "getuid") oraz hasattr(os, "geteuid"):
        # check process uid == effective uid
        jeżeli os.geteuid() != os.getuid():
            zwróć Nic
    jeżeli hasattr(os, "getgid") oraz hasattr(os, "getegid"):
        # check process gid == effective gid
        jeżeli os.getegid() != os.getgid():
            zwróć Nic

    zwróć Prawda

def getuserbase():
    """Returns the `user base` directory path.

    The `user base` directory can be used to store data. If the global
    variable ``USER_BASE`` jest nie initialized yet, this function will also set
    it.
    """
    global USER_BASE
    jeżeli USER_BASE jest nie Nic:
        zwróć USER_BASE
    z sysconfig zaimportuj get_config_var
    USER_BASE = get_config_var('userbase')
    zwróć USER_BASE

def getusersitepackages():
    """Returns the user-specific site-packages directory path.

    If the global variable ``USER_SITE`` jest nie initialized yet, this
    function will also set it.
    """
    global USER_SITE
    user_base = getuserbase() # this will also set USER_BASE

    jeżeli USER_SITE jest nie Nic:
        zwróć USER_SITE

    z sysconfig zaimportuj get_path

    jeżeli sys.platform == 'darwin':
        z sysconfig zaimportuj get_config_var
        jeżeli get_config_var('PYTHONFRAMEWORK'):
            USER_SITE = get_path('purelib', 'osx_framework_user')
            zwróć USER_SITE

    USER_SITE = get_path('purelib', '%s_user' % os.name)
    zwróć USER_SITE

def addusersitepackages(known_paths):
    """Add a per user site-package to sys.path

    Each user has its own python directory przy site-packages w the
    home directory.
    """
    # get the per user site-package path
    # this call will also make sure USER_BASE oraz USER_SITE are set
    user_site = getusersitepackages()

    jeżeli ENABLE_USER_SITE oraz os.path.isdir(user_site):
        addsitedir(user_site, known_paths)
    zwróć known_paths

def getsitepackages(prefixes=Nic):
    """Returns a list containing all global site-packages directories.

    For each directory present w ``prefixes`` (or the global ``PREFIXES``),
    this function will find its `site-packages` subdirectory depending on the
    system environment, oraz will zwróć a list of full paths.
    """
    sitepackages = []
    seen = set()

    jeżeli prefixes jest Nic:
        prefixes = PREFIXES

    dla prefix w prefixes:
        jeżeli nie prefix albo prefix w seen:
            kontynuuj
        seen.add(prefix)

        jeżeli os.sep == '/':
            sitepackages.append(os.path.join(prefix, "lib",
                                        "python" + sys.version[:3],
                                        "site-packages"))
        inaczej:
            sitepackages.append(prefix)
            sitepackages.append(os.path.join(prefix, "lib", "site-packages"))
        jeżeli sys.platform == "darwin":
            # dla framework builds *only* we add the standard Apple
            # locations.
            z sysconfig zaimportuj get_config_var
            framework = get_config_var("PYTHONFRAMEWORK")
            jeżeli framework:
                sitepackages.append(
                        os.path.join("/Library", framework,
                            sys.version[:3], "site-packages"))
    zwróć sitepackages

def addsitepackages(known_paths, prefixes=Nic):
    """Add site-packages to sys.path"""
    dla sitedir w getsitepackages(prefixes):
        jeżeli os.path.isdir(sitedir):
            addsitedir(sitedir, known_paths)

    zwróć known_paths

def setquit():
    """Define new builtins 'quit' oraz 'exit'.

    These are objects which make the interpreter exit when called.
    The repr of each object contains a hint at how it works.

    """
    jeżeli os.sep == ':':
        eof = 'Cmd-Q'
    albo_inaczej os.sep == '\\':
        eof = 'Ctrl-Z plus Return'
    inaczej:
        eof = 'Ctrl-D (i.e. EOF)'

    builtins.quit = _sitebuiltins.Quitter('quit', eof)
    builtins.exit = _sitebuiltins.Quitter('exit', eof)


def setcopyright():
    """Set 'copyright' oraz 'credits' w builtins"""
    builtins.copyright = _sitebuiltins._Printer("copyright", sys.copyright)
    jeżeli sys.platform[:4] == 'java':
        builtins.credits = _sitebuiltins._Printer(
            "credits",
            "Jython jest maintained by the Jython developers (www.jython.org).")
    inaczej:
        builtins.credits = _sitebuiltins._Printer("credits", """\
    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation oraz a cast of thousands
    dla supporting Python development.  See www.python.org dla more information.""")
    files, dirs = [], []
    # Not all modules are required to have a __file__ attribute.  See
    # PEP 420 dla more details.
    jeżeli hasattr(os, '__file__'):
        here = os.path.dirname(os.__file__)
        files.extend(["LICENSE.txt", "LICENSE"])
        dirs.extend([os.path.join(here, os.pardir), here, os.curdir])
    builtins.license = _sitebuiltins._Printer(
        "license",
        "See https://www.python.org/psf/license/",
        files, dirs)


def sethelper():
    builtins.help = _sitebuiltins._Helper()

def enablerlcompleter():
    """Enable default readline configuration on interactive prompts, by
    registering a sys.__interactivehook__.

    If the readline module can be imported, the hook will set the Tab key
    jako completion key oraz register ~/.python_history jako history file.
    This can be overriden w the sitecustomize albo usercustomize module,
    albo w a PYTHONSTARTUP file.
    """
    def register_readline():
        zaimportuj atexit
        spróbuj:
            zaimportuj readline
            zaimportuj rlcompleter
        wyjąwszy ImportError:
            zwróć

        # Reading the initialization (config) file may nie be enough to set a
        # completion key, so we set one first oraz then read the file.
        readline_doc = getattr(readline, '__doc__', '')
        jeżeli readline_doc jest nie Nic oraz 'libedit' w readline_doc:
            readline.parse_and_bind('bind ^I rl_complete')
        inaczej:
            readline.parse_and_bind('tab: complete')

        spróbuj:
            readline.read_init_file()
        wyjąwszy OSError:
            # An OSError here could have many causes, but the most likely one
            # jest that there's no .inputrc file (or .editrc file w the case of
            # Mac OS X + libedit) w the expected location.  In that case, we
            # want to ignore the exception.
            dalej

        jeżeli readline.get_current_history_length() == 0:
            # If no history was loaded, default to .python_history.
            # The guard jest necessary to avoid doubling history size at
            # each interpreter exit when readline was already configured
            # through a PYTHONSTARTUP hook, see:
            # http://bugs.python.org/issue5845#msg198636
            history = os.path.join(os.path.expanduser('~'),
                                   '.python_history')
            spróbuj:
                readline.read_history_file(history)
            wyjąwszy IOError:
                dalej
            atexit.register(readline.write_history_file, history)

    sys.__interactivehook__ = register_readline

def aliasmbcs():
    """On Windows, some default encodings are nie provided by Python,
    dopóki they are always available jako "mbcs" w each locale. Make
    them usable by aliasing to "mbcs" w such a case."""
    jeżeli sys.platform == 'win32':
        zaimportuj _bootlocale, codecs
        enc = _bootlocale.getpreferredencoding(Nieprawda)
        jeżeli enc.startswith('cp'):            # "cp***" ?
            spróbuj:
                codecs.lookup(enc)
            wyjąwszy LookupError:
                zaimportuj encodings
                encodings._cache[enc] = encodings._unknown
                encodings.aliases.aliases[enc] = 'mbcs'

CONFIG_LINE = r'^(?P<key>(\w|[-_])+)\s*=\s*(?P<value>.*)\s*$'

def venv(known_paths):
    global PREFIXES, ENABLE_USER_SITE

    env = os.environ
    jeżeli sys.platform == 'darwin' oraz '__PYVENV_LAUNCHER__' w env:
        executable = os.environ['__PYVENV_LAUNCHER__']
    inaczej:
        executable = sys.executable
    exe_dir, _ = os.path.split(os.path.abspath(executable))
    site_prefix = os.path.dirname(exe_dir)
    sys._home = Nic
    conf_basename = 'pyvenv.cfg'
    candidate_confs = [
        conffile dla conffile w (
            os.path.join(exe_dir, conf_basename),
            os.path.join(site_prefix, conf_basename)
            )
        jeżeli os.path.isfile(conffile)
        ]

    jeżeli candidate_confs:
        zaimportuj re
        config_line = re.compile(CONFIG_LINE)
        virtual_conf = candidate_confs[0]
        system_site = "true"
        przy open(virtual_conf) jako f:
            dla line w f:
                line = line.strip()
                m = config_line.match(line)
                jeżeli m:
                    d = m.groupdict()
                    key, value = d['key'].lower(), d['value']
                    jeżeli key == 'include-system-site-packages':
                        system_site = value.lower()
                    albo_inaczej key == 'home':
                        sys._home = value
                    albo_inaczej key == 'applocal' oraz value.lower() == 'true':
                        # App-local installs use the exe_dir jako prefix,
                        # nie one level higher, oraz do nie use system
                        # site packages.
                        site_prefix = exe_dir
                        system_site = 'false'

        sys.prefix = sys.exec_prefix = site_prefix

        # Doing this here ensures venv takes precedence over user-site
        addsitepackages(known_paths, [sys.prefix])

        # addsitepackages will process site_prefix again jeżeli its w PREFIXES,
        # but that's ok; known_paths will prevent anything being added twice
        jeżeli system_site == "true":
            PREFIXES.insert(0, sys.prefix)
        inaczej:
            PREFIXES = [sys.prefix]
            ENABLE_USER_SITE = Nieprawda

    zwróć known_paths


def execsitecustomize():
    """Run custom site specific code, jeżeli available."""
    spróbuj:
        zaimportuj sitecustomize
    wyjąwszy ImportError:
        dalej
    wyjąwszy Exception jako err:
        jeżeli os.environ.get("PYTHONVERBOSE"):
            sys.excepthook(*sys.exc_info())
        inaczej:
            sys.stderr.write(
                "Error w sitecustomize; set PYTHONVERBOSE dla traceback:\n"
                "%s: %s\n" %
                (err.__class__.__name__, err))


def execusercustomize():
    """Run custom user specific code, jeżeli available."""
    spróbuj:
        zaimportuj usercustomize
    wyjąwszy ImportError:
        dalej
    wyjąwszy Exception jako err:
        jeżeli os.environ.get("PYTHONVERBOSE"):
            sys.excepthook(*sys.exc_info())
        inaczej:
            sys.stderr.write(
                "Error w usercustomize; set PYTHONVERBOSE dla traceback:\n"
                "%s: %s\n" %
                (err.__class__.__name__, err))


def main():
    """Add standard site-specific directories to the module search path.

    This function jest called automatically when this module jest imported,
    unless the python interpreter was started przy the -S flag.
    """
    global ENABLE_USER_SITE

    abs_paths()
    known_paths = removeduppaths()
    known_paths = venv(known_paths)
    jeżeli ENABLE_USER_SITE jest Nic:
        ENABLE_USER_SITE = check_enableusersite()
    known_paths = addusersitepackages(known_paths)
    known_paths = addsitepackages(known_paths)
    setquit()
    setcopyright()
    sethelper()
    enablerlcompleter()
    aliasmbcs()
    execsitecustomize()
    jeżeli ENABLE_USER_SITE:
        execusercustomize()

# Prevent edition of sys.path when python was started przy -S oraz
# site jest imported later.
jeżeli nie sys.flags.no_site:
    main()

def _script():
    help = """\
    %s [--user-base] [--user-site]

    Without arguments print some useful information
    With arguments print the value of USER_BASE and/or USER_SITE separated
    by '%s'.

    Exit codes przy --user-base albo --user-site:
      0 - user site directory jest enabled
      1 - user site directory jest disabled by user
      2 - uses site directory jest disabled by super user
          albo dla security reasons
     >2 - unknown error
    """
    args = sys.argv[1:]
    jeżeli nie args:
        user_base = getuserbase()
        user_site = getusersitepackages()
        print("sys.path = [")
        dla dir w sys.path:
            print("    %r," % (dir,))
        print("]")
        print("USER_BASE: %r (%s)" % (user_base,
            "exists" jeżeli os.path.isdir(user_base) inaczej "doesn't exist"))
        print("USER_SITE: %r (%s)" % (user_site,
            "exists" jeżeli os.path.isdir(user_site) inaczej "doesn't exist"))
        print("ENABLE_USER_SITE: %r" %  ENABLE_USER_SITE)
        sys.exit(0)

    buffer = []
    jeżeli '--user-base' w args:
        buffer.append(USER_BASE)
    jeżeli '--user-site' w args:
        buffer.append(USER_SITE)

    jeżeli buffer:
        print(os.pathsep.join(buffer))
        jeżeli ENABLE_USER_SITE:
            sys.exit(0)
        albo_inaczej ENABLE_USER_SITE jest Nieprawda:
            sys.exit(1)
        albo_inaczej ENABLE_USER_SITE jest Nic:
            sys.exit(2)
        inaczej:
            sys.exit(3)
    inaczej:
        zaimportuj textwrap
        print(textwrap.dedent(help % (sys.argv[0], os.pathsep)))
        sys.exit(10)

jeżeli __name__ == '__main__':
    _script()
