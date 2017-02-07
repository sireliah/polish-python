"""Access to Python's configuration information."""

zaimportuj os
zaimportuj sys
z os.path zaimportuj pardir, realpath

__all__ = [
    'get_config_h_filename',
    'get_config_var',
    'get_config_vars',
    'get_makefile_filename',
    'get_path',
    'get_path_names',
    'get_paths',
    'get_platform',
    'get_python_version',
    'get_scheme_names',
    'parse_config_h',
]

_INSTALL_SCHEMES = {
    'posix_prefix': {
        'stdlib': '{installed_base}/lib/python{py_version_short}',
        'platstdlib': '{platbase}/lib/python{py_version_short}',
        'purelib': '{base}/lib/python{py_version_short}/site-packages',
        'platlib': '{platbase}/lib/python{py_version_short}/site-packages',
        'include':
            '{installed_base}/include/python{py_version_short}{abiflags}',
        'platinclude':
            '{installed_platbase}/include/python{py_version_short}{abiflags}',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'posix_home': {
        'stdlib': '{installed_base}/lib/python',
        'platstdlib': '{base}/lib/python',
        'purelib': '{base}/lib/python',
        'platlib': '{base}/lib/python',
        'include': '{installed_base}/include/python',
        'platinclude': '{installed_base}/include/python',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'nt': {
        'stdlib': '{installed_base}/Lib',
        'platstdlib': '{base}/Lib',
        'purelib': '{base}/Lib/site-packages',
        'platlib': '{base}/Lib/site-packages',
        'include': '{installed_base}/Include',
        'platinclude': '{installed_base}/Include',
        'scripts': '{base}/Scripts',
        'data': '{base}',
        },
    'nt_user': {
        'stdlib': '{userbase}/Python{py_version_nodot}',
        'platstdlib': '{userbase}/Python{py_version_nodot}',
        'purelib': '{userbase}/Python{py_version_nodot}/site-packages',
        'platlib': '{userbase}/Python{py_version_nodot}/site-packages',
        'include': '{userbase}/Python{py_version_nodot}/Include',
        'scripts': '{userbase}/Python{py_version_nodot}/Scripts',
        'data': '{userbase}',
        },
    'posix_user': {
        'stdlib': '{userbase}/lib/python{py_version_short}',
        'platstdlib': '{userbase}/lib/python{py_version_short}',
        'purelib': '{userbase}/lib/python{py_version_short}/site-packages',
        'platlib': '{userbase}/lib/python{py_version_short}/site-packages',
        'include': '{userbase}/include/python{py_version_short}',
        'scripts': '{userbase}/bin',
        'data': '{userbase}',
        },
    'osx_framework_user': {
        'stdlib': '{userbase}/lib/python',
        'platstdlib': '{userbase}/lib/python',
        'purelib': '{userbase}/lib/python/site-packages',
        'platlib': '{userbase}/lib/python/site-packages',
        'include': '{userbase}/include',
        'scripts': '{userbase}/bin',
        'data': '{userbase}',
        },
    }

_SCHEME_KEYS = ('stdlib', 'platstdlib', 'purelib', 'platlib', 'include',
                'scripts', 'data')

 # FIXME don't rely on sys.version here, its format jest an implementation detail
 # of CPython, use sys.version_info albo sys.hexversion
_PY_VERSION = sys.version.split()[0]
_PY_VERSION_SHORT = sys.version[:3]
_PY_VERSION_SHORT_NO_DOT = _PY_VERSION[0] + _PY_VERSION[2]
_PREFIX = os.path.normpath(sys.prefix)
_BASE_PREFIX = os.path.normpath(sys.base_prefix)
_EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
_BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)
_CONFIG_VARS = Nic
_USER_BASE = Nic


def _safe_realpath(path):
    spróbuj:
        zwróć realpath(path)
    wyjąwszy OSError:
        zwróć path

jeżeli sys.executable:
    _PROJECT_BASE = os.path.dirname(_safe_realpath(sys.executable))
inaczej:
    # sys.executable can be empty jeżeli argv[0] has been changed oraz Python jest
    # unable to retrieve the real program name
    _PROJECT_BASE = _safe_realpath(os.getcwd())

jeżeli (os.name == 'nt' oraz
    _PROJECT_BASE.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64'))):
    _PROJECT_BASE = _safe_realpath(os.path.join(_PROJECT_BASE, pardir, pardir))

# set dla cross builds
jeżeli "_PYTHON_PROJECT_BASE" w os.environ:
    _PROJECT_BASE = _safe_realpath(os.environ["_PYTHON_PROJECT_BASE"])

def _is_python_source_dir(d):
    dla fn w ("Setup.dist", "Setup.local"):
        jeżeli os.path.isfile(os.path.join(d, "Modules", fn)):
            zwróć Prawda
    zwróć Nieprawda

_sys_home = getattr(sys, '_home', Nic)
jeżeli (_sys_home oraz os.name == 'nt' oraz
    _sys_home.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64'))):
    _sys_home = os.path.dirname(os.path.dirname(_sys_home))
def is_python_build(check_home=Nieprawda):
    jeżeli check_home oraz _sys_home:
        zwróć _is_python_source_dir(_sys_home)
    zwróć _is_python_source_dir(_PROJECT_BASE)

_PYTHON_BUILD = is_python_build(Prawda)

jeżeli _PYTHON_BUILD:
    dla scheme w ('posix_prefix', 'posix_home'):
        _INSTALL_SCHEMES[scheme]['include'] = '{srcdir}/Include'
        _INSTALL_SCHEMES[scheme]['platinclude'] = '{projectbase}/.'


def _subst_vars(s, local_vars):
    spróbuj:
        zwróć s.format(**local_vars)
    wyjąwszy KeyError:
        spróbuj:
            zwróć s.format(**os.environ)
        wyjąwszy KeyError jako var:
            podnieś AttributeError('{%s}' % var)

def _extend_dict(target_dict, other_dict):
    target_keys = target_dict.keys()
    dla key, value w other_dict.items():
        jeżeli key w target_keys:
            kontynuuj
        target_dict[key] = value


def _expand_vars(scheme, vars):
    res = {}
    jeżeli vars jest Nic:
        vars = {}
    _extend_dict(vars, get_config_vars())

    dla key, value w _INSTALL_SCHEMES[scheme].items():
        jeżeli os.name w ('posix', 'nt'):
            value = os.path.expanduser(value)
        res[key] = os.path.normpath(_subst_vars(value, vars))
    zwróć res


def _get_default_scheme():
    jeżeli os.name == 'posix':
        # the default scheme dla posix jest posix_prefix
        zwróć 'posix_prefix'
    zwróć os.name


def _getuserbase():
    env_base = os.environ.get("PYTHONUSERBASE", Nic)

    def joinuser(*args):
        zwróć os.path.expanduser(os.path.join(*args))

    jeżeli os.name == "nt":
        base = os.environ.get("APPDATA") albo "~"
        jeżeli env_base:
            zwróć env_base
        inaczej:
            zwróć joinuser(base, "Python")

    jeżeli sys.platform == "darwin":
        framework = get_config_var("PYTHONFRAMEWORK")
        jeżeli framework:
            jeżeli env_base:
                zwróć env_base
            inaczej:
                zwróć joinuser("~", "Library", framework, "%d.%d" %
                                sys.version_info[:2])

    jeżeli env_base:
        zwróć env_base
    inaczej:
        zwróć joinuser("~", ".local")


def _parse_makefile(filename, vars=Nic):
    """Parse a Makefile-style file.

    A dictionary containing name/value pairs jest returned.  If an
    optional dictionary jest dalejed w jako the second argument, it jest
    used instead of a new dictionary.
    """
    # Regexes needed dla parsing Makefile (and similar syntaxes,
    # like old-style Setup files).
    zaimportuj re
    _variable_rx = re.compile("([a-zA-Z][a-zA-Z0-9_]+)\s*=\s*(.*)")
    _findvar1_rx = re.compile(r"\$\(([A-Za-z][A-Za-z0-9_]*)\)")
    _findvar2_rx = re.compile(r"\${([A-Za-z][A-Za-z0-9_]*)}")

    jeżeli vars jest Nic:
        vars = {}
    done = {}
    notdone = {}

    przy open(filename, errors="surrogateescape") jako f:
        lines = f.readlines()

    dla line w lines:
        jeżeli line.startswith('#') albo line.strip() == '':
            kontynuuj
        m = _variable_rx.match(line)
        jeżeli m:
            n, v = m.group(1, 2)
            v = v.strip()
            # `$$' jest a literal `$' w make
            tmpv = v.replace('$$', '')

            jeżeli "$" w tmpv:
                notdone[n] = v
            inaczej:
                spróbuj:
                    v = int(v)
                wyjąwszy ValueError:
                    # insert literal `$'
                    done[n] = v.replace('$$', '$')
                inaczej:
                    done[n] = v

    # do variable interpolation here
    variables = list(notdone.keys())

    # Variables przy a 'PY_' prefix w the makefile. These need to
    # be made available without that prefix through sysconfig.
    # Special care jest needed to ensure that variable expansion works, even
    # jeżeli the expansion uses the name without a prefix.
    renamed_variables = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS')

    dopóki len(variables) > 0:
        dla name w tuple(variables):
            value = notdone[name]
            m = _findvar1_rx.search(value) albo _findvar2_rx.search(value)
            jeżeli m jest nie Nic:
                n = m.group(1)
                found = Prawda
                jeżeli n w done:
                    item = str(done[n])
                albo_inaczej n w notdone:
                    # get it on a subsequent round
                    found = Nieprawda
                albo_inaczej n w os.environ:
                    # do it like make: fall back to environment
                    item = os.environ[n]

                albo_inaczej n w renamed_variables:
                    jeżeli (name.startswith('PY_') oraz
                        name[3:] w renamed_variables):
                        item = ""

                    albo_inaczej 'PY_' + n w notdone:
                        found = Nieprawda

                    inaczej:
                        item = str(done['PY_' + n])

                inaczej:
                    done[n] = item = ""

                jeżeli found:
                    after = value[m.end():]
                    value = value[:m.start()] + item + after
                    jeżeli "$" w after:
                        notdone[name] = value
                    inaczej:
                        spróbuj:
                            value = int(value)
                        wyjąwszy ValueError:
                            done[name] = value.strip()
                        inaczej:
                            done[name] = value
                        variables.remove(name)

                        jeżeli name.startswith('PY_') \
                        oraz name[3:] w renamed_variables:

                            name = name[3:]
                            jeżeli name nie w done:
                                done[name] = value

            inaczej:
                # bogus variable reference (e.g. "prefix=$/opt/python");
                # just drop it since we can't deal
                done[name] = value
                variables.remove(name)

    # strip spurious spaces
    dla k, v w done.items():
        jeżeli isinstance(v, str):
            done[k] = v.strip()

    # save the results w the global dictionary
    vars.update(done)
    zwróć vars


def get_makefile_filename():
    """Return the path of the Makefile."""
    jeżeli _PYTHON_BUILD:
        zwróć os.path.join(_sys_home albo _PROJECT_BASE, "Makefile")
    jeżeli hasattr(sys, 'abiflags'):
        config_dir_name = 'config-%s%s' % (_PY_VERSION_SHORT, sys.abiflags)
    inaczej:
        config_dir_name = 'config'
    zwróć os.path.join(get_path('stdlib'), config_dir_name, 'Makefile')

def _generate_posix_vars():
    """Generate the Python module containing build-time variables."""
    zaimportuj pprint
    vars = {}
    # load the installed Makefile:
    makefile = get_makefile_filename()
    spróbuj:
        _parse_makefile(makefile, vars)
    wyjąwszy OSError jako e:
        msg = "invalid Python installation: unable to open %s" % makefile
        jeżeli hasattr(e, "strerror"):
            msg = msg + " (%s)" % e.strerror
        podnieś OSError(msg)
    # load the installed pyconfig.h:
    config_h = get_config_h_filename()
    spróbuj:
        przy open(config_h) jako f:
            parse_config_h(f, vars)
    wyjąwszy OSError jako e:
        msg = "invalid Python installation: unable to open %s" % config_h
        jeżeli hasattr(e, "strerror"):
            msg = msg + " (%s)" % e.strerror
        podnieś OSError(msg)
    # On AIX, there are wrong paths to the linker scripts w the Makefile
    # -- these paths are relative to the Python source, but when installed
    # the scripts are w another directory.
    jeżeli _PYTHON_BUILD:
        vars['BLDSHARED'] = vars['LDSHARED']

    # There's a chicken-and-egg situation on OS X przy regards to the
    # _sysconfigdata module after the changes introduced by #15298:
    # get_config_vars() jest called by get_platform() jako part of the
    # `make pybuilddir.txt` target -- which jest a precursor to the
    # _sysconfigdata.py module being constructed.  Unfortunately,
    # get_config_vars() eventually calls _init_posix(), which attempts
    # to zaimportuj _sysconfigdata, which we won't have built yet.  In order
    # dla _init_posix() to work, jeżeli we're on Darwin, just mock up the
    # _sysconfigdata module manually oraz populate it przy the build vars.
    # This jest more than sufficient dla ensuring the subsequent call to
    # get_platform() succeeds.
    name = '_sysconfigdata'
    jeżeli 'darwin' w sys.platform:
        zaimportuj types
        module = types.ModuleType(name)
        module.build_time_vars = vars
        sys.modules[name] = module

    pybuilddir = 'build/lib.%s-%s' % (get_platform(), sys.version[:3])
    jeżeli hasattr(sys, "gettotalrefcount"):
        pybuilddir += '-pydebug'
    os.makedirs(pybuilddir, exist_ok=Prawda)
    destfile = os.path.join(pybuilddir, name + '.py')

    przy open(destfile, 'w', encoding='utf8') jako f:
        f.write('# system configuration generated oraz used by'
                ' the sysconfig module\n')
        f.write('build_time_vars = ')
        pprint.pprint(vars, stream=f)

    # Create file used dla sys.path fixup -- see Modules/getpath.c
    przy open('pybuilddir.txt', 'w', encoding='ascii') jako f:
        f.write(pybuilddir)

def _init_posix(vars):
    """Initialize the module jako appropriate dla POSIX systems."""
    # _sysconfigdata jest generated at build time, see _generate_posix_vars()
    z _sysconfigdata zaimportuj build_time_vars
    vars.update(build_time_vars)

def _init_non_posix(vars):
    """Initialize the module jako appropriate dla NT"""
    # set basic install directories
    vars['LIBDEST'] = get_path('stdlib')
    vars['BINLIBDEST'] = get_path('platstdlib')
    vars['INCLUDEPY'] = get_path('include')
    vars['EXT_SUFFIX'] = '.pyd'
    vars['EXE'] = '.exe'
    vars['VERSION'] = _PY_VERSION_SHORT_NO_DOT
    vars['BINDIR'] = os.path.dirname(_safe_realpath(sys.executable))

#
# public APIs
#


def parse_config_h(fp, vars=Nic):
    """Parse a config.h-style file.

    A dictionary containing name/value pairs jest returned.  If an
    optional dictionary jest dalejed w jako the second argument, it jest
    used instead of a new dictionary.
    """
    jeżeli vars jest Nic:
        vars = {}
    zaimportuj re
    define_rx = re.compile("#define ([A-Z][A-Za-z0-9_]+) (.*)\n")
    undef_rx = re.compile("/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n")

    dopóki Prawda:
        line = fp.readline()
        jeżeli nie line:
            przerwij
        m = define_rx.match(line)
        jeżeli m:
            n, v = m.group(1, 2)
            spróbuj:
                v = int(v)
            wyjąwszy ValueError:
                dalej
            vars[n] = v
        inaczej:
            m = undef_rx.match(line)
            jeżeli m:
                vars[m.group(1)] = 0
    zwróć vars


def get_config_h_filename():
    """Return the path of pyconfig.h."""
    jeżeli _PYTHON_BUILD:
        jeżeli os.name == "nt":
            inc_dir = os.path.join(_sys_home albo _PROJECT_BASE, "PC")
        inaczej:
            inc_dir = _sys_home albo _PROJECT_BASE
    inaczej:
        inc_dir = get_path('platinclude')
    zwróć os.path.join(inc_dir, 'pyconfig.h')


def get_scheme_names():
    """Return a tuple containing the schemes names."""
    zwróć tuple(sorted(_INSTALL_SCHEMES))


def get_path_names():
    """Return a tuple containing the paths names."""
    zwróć _SCHEME_KEYS


def get_paths(scheme=_get_default_scheme(), vars=Nic, expand=Prawda):
    """Return a mapping containing an install scheme.

    ``scheme`` jest the install scheme name. If nie provided, it will
    zwróć the default scheme dla the current platform.
    """
    jeżeli expand:
        zwróć _expand_vars(scheme, vars)
    inaczej:
        zwróć _INSTALL_SCHEMES[scheme]


def get_path(name, scheme=_get_default_scheme(), vars=Nic, expand=Prawda):
    """Return a path corresponding to the scheme.

    ``scheme`` jest the install scheme name.
    """
    zwróć get_paths(scheme, vars, expand)[name]


def get_config_vars(*args):
    """With no arguments, zwróć a dictionary of all configuration
    variables relevant dla the current platform.

    On Unix, this means every variable defined w Python's installed Makefile;
    On Windows it's a much smaller set.

    With arguments, zwróć a list of values that result z looking up
    each argument w the configuration variable dictionary.
    """
    global _CONFIG_VARS
    jeżeli _CONFIG_VARS jest Nic:
        _CONFIG_VARS = {}
        # Normalized versions of prefix oraz exec_prefix are handy to have;
        # w fact, these are the standard versions used most places w the
        # Distutils.
        _CONFIG_VARS['prefix'] = _PREFIX
        _CONFIG_VARS['exec_prefix'] = _EXEC_PREFIX
        _CONFIG_VARS['py_version'] = _PY_VERSION
        _CONFIG_VARS['py_version_short'] = _PY_VERSION_SHORT
        _CONFIG_VARS['py_version_nodot'] = _PY_VERSION[0] + _PY_VERSION[2]
        _CONFIG_VARS['installed_base'] = _BASE_PREFIX
        _CONFIG_VARS['base'] = _PREFIX
        _CONFIG_VARS['installed_platbase'] = _BASE_EXEC_PREFIX
        _CONFIG_VARS['platbase'] = _EXEC_PREFIX
        _CONFIG_VARS['projectbase'] = _PROJECT_BASE
        spróbuj:
            _CONFIG_VARS['abiflags'] = sys.abiflags
        wyjąwszy AttributeError:
            # sys.abiflags may nie be defined on all platforms.
            _CONFIG_VARS['abiflags'] = ''

        jeżeli os.name == 'nt':
            _init_non_posix(_CONFIG_VARS)
        jeżeli os.name == 'posix':
            _init_posix(_CONFIG_VARS)
        # For backward compatibility, see issue19555
        SO = _CONFIG_VARS.get('EXT_SUFFIX')
        jeżeli SO jest nie Nic:
            _CONFIG_VARS['SO'] = SO
        # Setting 'userbase' jest done below the call to the
        # init function to enable using 'get_config_var' w
        # the init-function.
        _CONFIG_VARS['userbase'] = _getuserbase()

        # Always convert srcdir to an absolute path
        srcdir = _CONFIG_VARS.get('srcdir', _PROJECT_BASE)
        jeżeli os.name == 'posix':
            jeżeli _PYTHON_BUILD:
                # If srcdir jest a relative path (typically '.' albo '..')
                # then it should be interpreted relative to the directory
                # containing Makefile.
                base = os.path.dirname(get_makefile_filename())
                srcdir = os.path.join(base, srcdir)
            inaczej:
                # srcdir jest nie meaningful since the installation jest
                # spread about the filesystem.  We choose the
                # directory containing the Makefile since we know it
                # exists.
                srcdir = os.path.dirname(get_makefile_filename())
        _CONFIG_VARS['srcdir'] = _safe_realpath(srcdir)

        # OS X platforms require special customization to handle
        # multi-architecture, multi-os-version installers
        jeżeli sys.platform == 'darwin':
            zaimportuj _osx_support
            _osx_support.customize_config_vars(_CONFIG_VARS)

    jeżeli args:
        vals = []
        dla name w args:
            vals.append(_CONFIG_VARS.get(name))
        zwróć vals
    inaczej:
        zwróć _CONFIG_VARS


def get_config_var(name):
    """Return the value of a single variable using the dictionary returned by
    'get_config_vars()'.

    Equivalent to get_config_vars().get(name)
    """
    jeżeli name == 'SO':
        zaimportuj warnings
        warnings.warn('SO jest deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    zwróć get_config_vars().get(name)


def get_platform():
    """Return a string that identifies the current platform.

    This jest used mainly to distinguish platform-specific build directories oraz
    platform-specific built distributions.  Typically includes the OS name
    oraz version oraz the architecture (as supplied by 'os.uname()'),
    although the exact information included depends on the OS; eg. dla IRIX
    the architecture isn't particularly important (IRIX only runs on SGI
    hardware), but dla Linux the kernel version isn't particularly
    important.

    Examples of returned values:
       linux-i586
       linux-alpha (?)
       solaris-2.6-sun4u
       irix-5.3
       irix64-6.2

    Windows will zwróć one of:
       win-amd64 (64bit Windows on AMD64 (aka x86_64, Intel64, EM64T, etc)
       win-ia64 (64bit Windows on Itanium)
       win32 (all others - specifically, sys.platform jest returned)

    For other non-POSIX platforms, currently just returns 'sys.platform'.
    """
    jeżeli os.name == 'nt':
        # sniff sys.version dla architecture.
        prefix = " bit ("
        i = sys.version.find(prefix)
        jeżeli i == -1:
            zwróć sys.platform
        j = sys.version.find(")", i)
        look = sys.version[i+len(prefix):j].lower()
        jeżeli look == 'amd64':
            zwróć 'win-amd64'
        jeżeli look == 'itanium':
            zwróć 'win-ia64'
        zwróć sys.platform

    jeżeli os.name != "posix" albo nie hasattr(os, 'uname'):
        # XXX what about the architecture? NT jest Intel albo Alpha
        zwróć sys.platform

    # Set dla cross builds explicitly
    jeżeli "_PYTHON_HOST_PLATFORM" w os.environ:
        zwróć os.environ["_PYTHON_HOST_PLATFORM"]

    # Try to distinguish various flavours of Unix
    osname, host, release, version, machine = os.uname()

    # Convert the OS name to lowercase, remove '/' characters
    # (to accommodate BSD/OS), oraz translate spaces (dla "Power Macintosh")
    osname = osname.lower().replace('/', '')
    machine = machine.replace(' ', '_')
    machine = machine.replace('/', '-')

    jeżeli osname[:5] == "linux":
        # At least on Linux/Intel, 'machine' jest the processor --
        # i386, etc.
        # XXX what about Alpha, SPARC, etc?
        zwróć  "%s-%s" % (osname, machine)
    albo_inaczej osname[:5] == "sunos":
        jeżeli release[0] >= "5":           # SunOS 5 == Solaris 2
            osname = "solaris"
            release = "%d.%s" % (int(release[0]) - 3, release[2:])
            # We can't use "platform.architecture()[0]" because a
            # bootstrap problem. We use a dict to get an error
            # jeżeli some suspicious happens.
            bitness = {2147483647:"32bit", 9223372036854775807:"64bit"}
            machine += ".%s" % bitness[sys.maxsize]
        # fall through to standard osname-release-machine representation
    albo_inaczej osname[:4] == "irix":              # could be "irix64"!
        zwróć "%s-%s" % (osname, release)
    albo_inaczej osname[:3] == "aix":
        zwróć "%s-%s.%s" % (osname, version, release)
    albo_inaczej osname[:6] == "cygwin":
        osname = "cygwin"
        zaimportuj re
        rel_re = re.compile(r'[\d.]+')
        m = rel_re.match(release)
        jeżeli m:
            release = m.group()
    albo_inaczej osname[:6] == "darwin":
        zaimportuj _osx_support
        osname, release, machine = _osx_support.get_platform_osx(
                                            get_config_vars(),
                                            osname, release, machine)

    zwróć "%s-%s-%s" % (osname, release, machine)


def get_python_version():
    zwróć _PY_VERSION_SHORT


def _print_dict(title, data):
    dla index, (key, value) w enumerate(sorted(data.items())):
        jeżeli index == 0:
            #print('%s: ' % (title))
            dalej
        #print('\t%s = "%s"' % (key, value))


def _main():
    """Display all information sysconfig detains."""
    jeżeli '--generate-posix-vars' w sys.argv:
        _generate_posix_vars()
        zwróć
    print('Platform: "%s"' % get_platform())
    print('Python version: "%s"' % get_python_version())
    print('Current installation scheme: "%s"' % _get_default_scheme())
    print()
    _print_dict('Paths', get_paths())
    print()
    _print_dict('Variables', get_config_vars())


jeżeli __name__ == '__main__':
    _main()
