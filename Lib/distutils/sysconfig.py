"""Provide access to Python's configuration information.  The specific
configuration variables available depend heavily on the platform oraz
configuration.  The values may be retrieved using
get_config_var(name), oraz the list of variables jest available via
get_config_vars().keys().  Additional convenience functions are also
available.

Written by:   Fred L. Drake, Jr.
Email:        <fdrake@acm.org>
"""

zaimportuj _imp
zaimportuj os
zaimportuj re
zaimportuj sys

z .errors zaimportuj DistutilsPlatformError

# These are needed w a couple of spots, so just compute them once.
PREFIX = os.path.normpath(sys.prefix)
EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
BASE_PREFIX = os.path.normpath(sys.base_prefix)
BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)

# Path to the base directory of the project. On Windows the binary may
# live w project/PCBuild/win32 albo project/PCBuild/amd64.
# set dla cross builds
jeżeli "_PYTHON_PROJECT_BASE" w os.environ:
    project_base = os.path.abspath(os.environ["_PYTHON_PROJECT_BASE"])
inaczej:
    project_base = os.path.dirname(os.path.abspath(sys.executable))
jeżeli (os.name == 'nt' oraz
    project_base.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64'))):
    project_base = os.path.dirname(os.path.dirname(project_base))

# python_build: (Boolean) jeżeli true, we're either building Python albo
# building an extension przy an un-installed Python, so we use
# different (hard-wired) directories.
# Setup.local jest available dla Makefile builds including VPATH builds,
# Setup.dist jest available on Windows
def _is_python_source_dir(d):
    dla fn w ("Setup.dist", "Setup.local"):
        jeżeli os.path.isfile(os.path.join(d, "Modules", fn)):
            zwróć Prawda
    zwróć Nieprawda
_sys_home = getattr(sys, '_home', Nic)
jeżeli (_sys_home oraz os.name == 'nt' oraz
    _sys_home.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64'))):
    _sys_home = os.path.dirname(os.path.dirname(_sys_home))
def _python_build():
    jeżeli _sys_home:
        zwróć _is_python_source_dir(_sys_home)
    zwróć _is_python_source_dir(project_base)
python_build = _python_build()

# Calculate the build qualifier flags jeżeli they are defined.  Adding the flags
# to the include oraz lib directories only makes sense dla an installation, nie
# an in-source build.
build_flags = ''
spróbuj:
    jeżeli nie python_build:
        build_flags = sys.abiflags
wyjąwszy AttributeError:
    # It's nie a configure-based build, so the sys module doesn't have
    # this attribute, which jest fine.
    dalej

def get_python_version():
    """Return a string containing the major oraz minor Python version,
    leaving off the patchlevel.  Sample zwróć values could be '1.5'
    albo '2.2'.
    """
    zwróć sys.version[:3]


def get_python_inc(plat_specific=0, prefix=Nic):
    """Return the directory containing installed Python header files.

    If 'plat_specific' jest false (the default), this jest the path to the
    non-platform-specific header files, i.e. Python.h oraz so on;
    otherwise, this jest the path to platform-specific header files
    (namely pyconfig.h).

    If 'prefix' jest supplied, use it instead of sys.base_prefix albo
    sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    jeżeli prefix jest Nic:
        prefix = plat_specific oraz BASE_EXEC_PREFIX albo BASE_PREFIX
    jeżeli os.name == "posix":
        jeżeli python_build:
            # Assume the executable jest w the build directory.  The
            # pyconfig.h file should be w the same directory.  Since
            # the build directory may nie be the source directory, we
            # must use "srcdir" z the makefile to find the "Include"
            # directory.
            base = _sys_home albo project_base
            jeżeli plat_specific:
                zwróć base
            jeżeli _sys_home:
                incdir = os.path.join(_sys_home, get_config_var('AST_H_DIR'))
            inaczej:
                incdir = os.path.join(get_config_var('srcdir'), 'Include')
            zwróć os.path.normpath(incdir)
        python_dir = 'python' + get_python_version() + build_flags
        zwróć os.path.join(prefix, "include", python_dir)
    albo_inaczej os.name == "nt":
        zwróć os.path.join(prefix, "include")
    inaczej:
        podnieś DistutilsPlatformError(
            "I don't know where Python installs its C header files "
            "on platform '%s'" % os.name)


def get_python_lib(plat_specific=0, standard_lib=0, prefix=Nic):
    """Return the directory containing the Python library (standard albo
    site additions).

    If 'plat_specific' jest true, zwróć the directory containing
    platform-specific modules, i.e. any module z a non-pure-Python
    module distribution; otherwise, zwróć the platform-shared library
    directory.  If 'standard_lib' jest true, zwróć the directory
    containing standard Python library modules; otherwise, zwróć the
    directory dla site-specific modules.

    If 'prefix' jest supplied, use it instead of sys.base_prefix albo
    sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    jeżeli prefix jest Nic:
        jeżeli standard_lib:
            prefix = plat_specific oraz BASE_EXEC_PREFIX albo BASE_PREFIX
        inaczej:
            prefix = plat_specific oraz EXEC_PREFIX albo PREFIX

    jeżeli os.name == "posix":
        libpython = os.path.join(prefix,
                                 "lib", "python" + get_python_version())
        jeżeli standard_lib:
            zwróć libpython
        inaczej:
            zwróć os.path.join(libpython, "site-packages")
    albo_inaczej os.name == "nt":
        jeżeli standard_lib:
            zwróć os.path.join(prefix, "Lib")
        inaczej:
            zwróć os.path.join(prefix, "Lib", "site-packages")
    inaczej:
        podnieś DistutilsPlatformError(
            "I don't know where Python installs its library "
            "on platform '%s'" % os.name)



def customize_compiler(compiler):
    """Do any platform-specific customization of a CCompiler instance.

    Mainly needed on Unix, so we can plug w the information that
    varies across Unices oraz jest stored w Python's Makefile.
    """
    jeżeli compiler.compiler_type == "unix":
        jeżeli sys.platform == "darwin":
            # Perform first-time customization of compiler-related
            # config vars on OS X now that we know we need a compiler.
            # This jest primarily to support Pythons z binary
            # installers.  The kind oraz paths to build tools on
            # the user system may vary significantly z the system
            # that Python itself was built on.  Also the user OS
            # version oraz build tools may nie support the same set
            # of CPU architectures dla universal builds.
            global _config_vars
            # Use get_config_var() to ensure _config_vars jest initialized.
            jeżeli nie get_config_var('CUSTOMIZED_OSX_COMPILER'):
                zaimportuj _osx_support
                _osx_support.customize_compiler(_config_vars)
                _config_vars['CUSTOMIZED_OSX_COMPILER'] = 'Prawda'

        (cc, cxx, opt, cflags, ccshared, ldshared, shlib_suffix, ar, ar_flags) = \
            get_config_vars('CC', 'CXX', 'OPT', 'CFLAGS',
                            'CCSHARED', 'LDSHARED', 'SHLIB_SUFFIX', 'AR', 'ARFLAGS')

        jeżeli 'CC' w os.environ:
            newcc = os.environ['CC']
            jeżeli (sys.platform == 'darwin'
                    oraz 'LDSHARED' nie w os.environ
                    oraz ldshared.startswith(cc)):
                # On OS X, jeżeli CC jest overridden, use that jako the default
                #       command dla LDSHARED jako well
                ldshared = newcc + ldshared[len(cc):]
            cc = newcc
        jeżeli 'CXX' w os.environ:
            cxx = os.environ['CXX']
        jeżeli 'LDSHARED' w os.environ:
            ldshared = os.environ['LDSHARED']
        jeżeli 'CPP' w os.environ:
            cpp = os.environ['CPP']
        inaczej:
            cpp = cc + " -E"           # nie always
        jeżeli 'LDFLAGS' w os.environ:
            ldshared = ldshared + ' ' + os.environ['LDFLAGS']
        jeżeli 'CFLAGS' w os.environ:
            cflags = opt + ' ' + os.environ['CFLAGS']
            ldshared = ldshared + ' ' + os.environ['CFLAGS']
        jeżeli 'CPPFLAGS' w os.environ:
            cpp = cpp + ' ' + os.environ['CPPFLAGS']
            cflags = cflags + ' ' + os.environ['CPPFLAGS']
            ldshared = ldshared + ' ' + os.environ['CPPFLAGS']
        jeżeli 'AR' w os.environ:
            ar = os.environ['AR']
        jeżeli 'ARFLAGS' w os.environ:
            archiver = ar + ' ' + os.environ['ARFLAGS']
        inaczej:
            archiver = ar + ' ' + ar_flags

        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ccshared,
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc,
            archiver=archiver)

        compiler.shared_lib_extension = shlib_suffix


def get_config_h_filename():
    """Return full pathname of installed pyconfig.h file."""
    jeżeli python_build:
        jeżeli os.name == "nt":
            inc_dir = os.path.join(_sys_home albo project_base, "PC")
        inaczej:
            inc_dir = _sys_home albo project_base
    inaczej:
        inc_dir = get_python_inc(plat_specific=1)

    zwróć os.path.join(inc_dir, 'pyconfig.h')


def get_makefile_filename():
    """Return full pathname of installed Makefile z the Python build."""
    jeżeli python_build:
        zwróć os.path.join(_sys_home albo project_base, "Makefile")
    lib_dir = get_python_lib(plat_specific=0, standard_lib=1)
    config_file = 'config-{}{}'.format(get_python_version(), build_flags)
    zwróć os.path.join(lib_dir, config_file, 'Makefile')


def parse_config_h(fp, g=Nic):
    """Parse a config.h-style file.

    A dictionary containing name/value pairs jest returned.  If an
    optional dictionary jest dalejed w jako the second argument, it jest
    used instead of a new dictionary.
    """
    jeżeli g jest Nic:
        g = {}
    define_rx = re.compile("#define ([A-Z][A-Za-z0-9_]+) (.*)\n")
    undef_rx = re.compile("/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n")
    #
    dopóki Prawda:
        line = fp.readline()
        jeżeli nie line:
            przerwij
        m = define_rx.match(line)
        jeżeli m:
            n, v = m.group(1, 2)
            spróbuj: v = int(v)
            wyjąwszy ValueError: dalej
            g[n] = v
        inaczej:
            m = undef_rx.match(line)
            jeżeli m:
                g[m.group(1)] = 0
    zwróć g


# Regexes needed dla parsing Makefile (and similar syntaxes,
# like old-style Setup files).
_variable_rx = re.compile("([a-zA-Z][a-zA-Z0-9_]+)\s*=\s*(.*)")
_findvar1_rx = re.compile(r"\$\(([A-Za-z][A-Za-z0-9_]*)\)")
_findvar2_rx = re.compile(r"\${([A-Za-z][A-Za-z0-9_]*)}")

def parse_makefile(fn, g=Nic):
    """Parse a Makefile-style file.

    A dictionary containing name/value pairs jest returned.  If an
    optional dictionary jest dalejed w jako the second argument, it jest
    used instead of a new dictionary.
    """
    z distutils.text_file zaimportuj TextFile
    fp = TextFile(fn, strip_comments=1, skip_blanks=1, join_lines=1, errors="surrogateescape")

    jeżeli g jest Nic:
        g = {}
    done = {}
    notdone = {}

    dopóki Prawda:
        line = fp.readline()
        jeżeli line jest Nic: # eof
            przerwij
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

    # Variables przy a 'PY_' prefix w the makefile. These need to
    # be made available without that prefix through sysconfig.
    # Special care jest needed to ensure that variable expansion works, even
    # jeżeli the expansion uses the name without a prefix.
    renamed_variables = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS')

    # do variable interpolation here
    dopóki notdone:
        dla name w list(notdone):
            value = notdone[name]
            m = _findvar1_rx.search(value) albo _findvar2_rx.search(value)
            jeżeli m:
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
                    jeżeli name.startswith('PY_') oraz name[3:] w renamed_variables:
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
                        spróbuj: value = int(value)
                        wyjąwszy ValueError:
                            done[name] = value.strip()
                        inaczej:
                            done[name] = value
                        usuń notdone[name]

                        jeżeli name.startswith('PY_') \
                            oraz name[3:] w renamed_variables:

                            name = name[3:]
                            jeżeli name nie w done:
                                done[name] = value
            inaczej:
                # bogus variable reference; just drop it since we can't deal
                usuń notdone[name]

    fp.close()

    # strip spurious spaces
    dla k, v w done.items():
        jeżeli isinstance(v, str):
            done[k] = v.strip()

    # save the results w the global dictionary
    g.update(done)
    zwróć g


def expand_makefile_vars(s, vars):
    """Expand Makefile-style variables -- "${foo}" albo "$(foo)" -- w
    'string' according to 'vars' (a dictionary mapping variable names to
    values).  Variables nie present w 'vars' are silently expanded to the
    empty string.  The variable values w 'vars' should nie contain further
    variable expansions; jeżeli 'vars' jest the output of 'parse_makefile()',
    you're fine.  Returns a variable-expanded version of 's'.
    """

    # This algorithm does multiple expansion, so jeżeli vars['foo'] contains
    # "${bar}", it will expand ${foo} to ${bar}, oraz then expand
    # ${bar}... oraz so forth.  This jest fine jako long jako 'vars' comes from
    # 'parse_makefile()', which takes care of such expansions eagerly,
    # according to make's variable expansion semantics.

    dopóki Prawda:
        m = _findvar1_rx.search(s) albo _findvar2_rx.search(s)
        jeżeli m:
            (beg, end) = m.span()
            s = s[0:beg] + vars.get(m.group(1)) + s[end:]
        inaczej:
            przerwij
    zwróć s


_config_vars = Nic

def _init_posix():
    """Initialize the module jako appropriate dla POSIX systems."""
    g = {}
    # load the installed Makefile:
    spróbuj:
        filename = get_makefile_filename()
        parse_makefile(filename, g)
    wyjąwszy OSError jako msg:
        my_msg = "invalid Python installation: unable to open %s" % filename
        jeżeli hasattr(msg, "strerror"):
            my_msg = my_msg + " (%s)" % msg.strerror

        podnieś DistutilsPlatformError(my_msg)

    # load the installed pyconfig.h:
    spróbuj:
        filename = get_config_h_filename()
        przy open(filename) jako file:
            parse_config_h(file, g)
    wyjąwszy OSError jako msg:
        my_msg = "invalid Python installation: unable to open %s" % filename
        jeżeli hasattr(msg, "strerror"):
            my_msg = my_msg + " (%s)" % msg.strerror

        podnieś DistutilsPlatformError(my_msg)

    # On AIX, there are wrong paths to the linker scripts w the Makefile
    # -- these paths are relative to the Python source, but when installed
    # the scripts are w another directory.
    jeżeli python_build:
        g['LDSHARED'] = g['BLDSHARED']

    global _config_vars
    _config_vars = g


def _init_nt():
    """Initialize the module jako appropriate dla NT"""
    g = {}
    # set basic install directories
    g['LIBDEST'] = get_python_lib(plat_specific=0, standard_lib=1)
    g['BINLIBDEST'] = get_python_lib(plat_specific=1, standard_lib=1)

    # XXX hmmm.. a normal install puts include files here
    g['INCLUDEPY'] = get_python_inc(plat_specific=0)

    g['EXT_SUFFIX'] = _imp.extension_suffixes()[0]
    g['EXE'] = ".exe"
    g['VERSION'] = get_python_version().replace(".", "")
    g['BINDIR'] = os.path.dirname(os.path.abspath(sys.executable))

    global _config_vars
    _config_vars = g


def get_config_vars(*args):
    """With no arguments, zwróć a dictionary of all configuration
    variables relevant dla the current platform.  Generally this includes
    everything needed to build extensions oraz install both pure modules oraz
    extensions.  On Unix, this means every variable defined w Python's
    installed Makefile; on Windows it's a much smaller set.

    With arguments, zwróć a list of values that result z looking up
    each argument w the configuration variable dictionary.
    """
    global _config_vars
    jeżeli _config_vars jest Nic:
        func = globals().get("_init_" + os.name)
        jeżeli func:
            func()
        inaczej:
            _config_vars = {}

        # Normalized versions of prefix oraz exec_prefix are handy to have;
        # w fact, these are the standard versions used most places w the
        # Distutils.
        _config_vars['prefix'] = PREFIX
        _config_vars['exec_prefix'] = EXEC_PREFIX

        # For backward compatibility, see issue19555
        SO = _config_vars.get('EXT_SUFFIX')
        jeżeli SO jest nie Nic:
            _config_vars['SO'] = SO

        # Always convert srcdir to an absolute path
        srcdir = _config_vars.get('srcdir', project_base)
        jeżeli os.name == 'posix':
            jeżeli python_build:
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
        _config_vars['srcdir'] = os.path.abspath(os.path.normpath(srcdir))

        # Convert srcdir into an absolute path jeżeli it appears necessary.
        # Normally it jest relative to the build directory.  However, during
        # testing, dla example, we might be running a non-installed python
        # z a different directory.
        jeżeli python_build oraz os.name == "posix":
            base = project_base
            jeżeli (nie os.path.isabs(_config_vars['srcdir']) oraz
                base != os.getcwd()):
                # srcdir jest relative oraz we are nie w the same directory
                # jako the executable. Assume executable jest w the build
                # directory oraz make srcdir absolute.
                srcdir = os.path.join(base, _config_vars['srcdir'])
                _config_vars['srcdir'] = os.path.normpath(srcdir)

        # OS X platforms require special customization to handle
        # multi-architecture, multi-os-version installers
        jeżeli sys.platform == 'darwin':
            zaimportuj _osx_support
            _osx_support.customize_config_vars(_config_vars)

    jeżeli args:
        vals = []
        dla name w args:
            vals.append(_config_vars.get(name))
        zwróć vals
    inaczej:
        zwróć _config_vars

def get_config_var(name):
    """Return the value of a single variable using the dictionary
    returned by 'get_config_vars()'.  Equivalent to
    get_config_vars().get(name)
    """
    jeżeli name == 'SO':
        zaimportuj warnings
        warnings.warn('SO jest deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    zwróć get_config_vars().get(name)
