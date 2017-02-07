#!/usr/bin/env python
"""
This script jest used to build "official" universal installers on Mac OS X.
It requires at least Mac OS X 10.5, Xcode 3, oraz the 10.4u SDK for
32-bit builds.  64-bit albo four-way universal builds require at least
OS X 10.5 oraz the 10.5 SDK.

Please ensure that this script keeps working przy Python 2.5, to avoid
bootstrap issues (/usr/bin/python jest Python 2.5 on OSX 10.5).  Sphinx,
which jest used to build the documentation, currently requires at least
Python 2.4.  However, jako of Python 3.4.1, Doc builds require an external
sphinx-build oraz the current versions of Sphinx now require at least
Python 2.6.

In addition to what jest supplied przy OS X 10.5+ oraz Xcode 3+, the script
requires an installed version of hg oraz a third-party version of
Tcl/Tk 8.4 (dla OS X 10.4 oraz 10.5 deployment targets) albo Tcl/TK 8.5
(dla 10.6 albo later) installed w /Library/Frameworks.  When installed,
the Python built by this script will attempt to dynamically link first to
Tcl oraz Tk frameworks w /Library/Frameworks jeżeli available otherwise fall
back to the ones w /System/Library/Framework.  For the build, we recommend
installing the most recent ActiveTcl 8.4 albo 8.5 version.

32-bit-only installer builds are still possible on OS X 10.4 przy Xcode 2.5
and the installation of additional components, such jako a newer Python
(2.5 jest needed dla Python parser updates), hg, oraz dla the documentation
build either svn (pre-3.4.1) albo sphinx-build (3.4.1 oraz later).

Usage: see USAGE variable w the script.
"""
zaimportuj platform, os, sys, getopt, textwrap, shutil, stat, time, pwd, grp
spróbuj:
    zaimportuj urllib2 jako urllib_request
wyjąwszy ImportError:
    zaimportuj urllib.request jako urllib_request

STAT_0o755 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP |                stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

INCLUDE_TIMESTAMP = 1
VERBOSE = 1

z plistlib zaimportuj Plist

spróbuj:
    z plistlib zaimportuj writePlist
wyjąwszy ImportError:
    # We're run using python2.3
    def writePlist(plist, path):
        plist.write(path)

def shellQuote(value):
    """
    Return the string value w a form that can safely be inserted into
    a shell command.
    """
    zwróć "'%s'"%(value.replace("'", "'\"'\"'"))

def grepValue(fn, variable):
    """
    Return the unquoted value of a variable z a file..
    QUOTED_VALUE='quotes'    -> str('quotes')
    UNQUOTED_VALUE=noquotes  -> str('noquotes')
    """
    variable = variable + '='
    dla ln w open(fn, 'r'):
        jeżeli ln.startswith(variable):
            value = ln[len(variable):].strip()
            zwróć value.strip("\"'")
    podnieś RuntimeError("Cannot find variable %s" % variable[:-1])

_cache_getVersion = Nic

def getVersion():
    global _cache_getVersion
    jeżeli _cache_getVersion jest Nic:
        _cache_getVersion = grepValue(
            os.path.join(SRCDIR, 'configure'), 'PACKAGE_VERSION')
    zwróć _cache_getVersion

def getVersionMajorMinor():
    zwróć tuple([int(n) dla n w getVersion().split('.', 2)])

_cache_getFullVersion = Nic

def getFullVersion():
    global _cache_getFullVersion
    jeżeli _cache_getFullVersion jest nie Nic:
        zwróć _cache_getFullVersion
    fn = os.path.join(SRCDIR, 'Include', 'patchlevel.h')
    dla ln w open(fn):
        jeżeli 'PY_VERSION' w ln:
            _cache_getFullVersion = ln.split()[-1][1:-1]
            zwróć _cache_getFullVersion
    podnieś RuntimeError("Cannot find full version??")

FW_PREFIX = ["Library", "Frameworks", "Python.framework"]
FW_VERSION_PREFIX = "--undefined--" # initialized w parseOptions

# The directory we'll use to create the build (will be erased oraz recreated)
WORKDIR = "/tmp/_py"

# The directory we'll use to store third-party sources. Set this to something
# inaczej jeżeli you don't want to re-fetch required libraries every time.
DEPSRC = os.path.join(WORKDIR, 'third-party')
DEPSRC = os.path.expanduser('~/Universal/other-sources')

# Location of the preferred SDK

### There are some issues przy the SDK selection below here,
### The resulting binary doesn't work on all platforms that
### it should. Always default to the 10.4u SDK until that
### issue jest resolved.
###
##jeżeli int(os.uname()[2].split('.')[0]) == 8:
##    # Explicitly use the 10.4u (universal) SDK when
##    # building on 10.4, the system headers are nie
##    # useable dla a universal build
##    SDKPATH = "/Developer/SDKs/MacOSX10.4u.sdk"
##inaczej:
##    SDKPATH = "/"

SDKPATH = "/Developer/SDKs/MacOSX10.4u.sdk"

universal_opts_map = { '32-bit': ('i386', 'ppc',),
                       '64-bit': ('x86_64', 'ppc64',),
                       'intel':  ('i386', 'x86_64'),
                       '3-way':  ('ppc', 'i386', 'x86_64'),
                       'all':    ('i386', 'ppc', 'x86_64', 'ppc64',) }
default_target_map = {
        '64-bit': '10.5',
        '3-way': '10.5',
        'intel': '10.5',
        'all': '10.5',
}

UNIVERSALOPTS = tuple(universal_opts_map.keys())

UNIVERSALARCHS = '32-bit'

ARCHLIST = universal_opts_map[UNIVERSALARCHS]

# Source directory (assume we're w Mac/BuildScript)
SRCDIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__
        ))))

# $MACOSX_DEPLOYMENT_TARGET -> minimum OS X level
DEPTARGET = '10.3'

def getDeptargetTuple():
    zwróć tuple([int(n) dla n w DEPTARGET.split('.')[0:2]])

def getTargetCompilers():
    target_cc_map = {
        '10.3': ('gcc-4.0', 'g++-4.0'),
        '10.4': ('gcc-4.0', 'g++-4.0'),
        '10.5': ('gcc-4.2', 'g++-4.2'),
        '10.6': ('gcc-4.2', 'g++-4.2'),
    }
    zwróć target_cc_map.get(DEPTARGET, ('clang', 'clang++') )

CC, CXX = getTargetCompilers()

PYTHON_3 = getVersionMajorMinor() >= (3, 0)

USAGE = textwrap.dedent("""\
    Usage: build_python [options]

    Options:
    -? albo -h:            Show this message
    -b DIR
    --build-dir=DIR:     Create build here (default: %(WORKDIR)r)
    --third-party=DIR:   Store third-party sources here (default: %(DEPSRC)r)
    --sdk-path=DIR:      Location of the SDK (default: %(SDKPATH)r)
    --src-dir=DIR:       Location of the Python sources (default: %(SRCDIR)r)
    --dep-target=10.n    OS X deployment target (default: %(DEPTARGET)r)
    --universal-archs=x  universal architectures (options: %(UNIVERSALOPTS)r, default: %(UNIVERSALARCHS)r)
""")% globals()

# Dict of object file names przy shared library names to check after building.
# This jest to ensure that we ended up dynamically linking przy the shared
# library paths oraz versions we expected.  For example:
#   EXPECTED_SHARED_LIBS['_tkinter.so'] = [
#                       '/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl',
#                       '/Library/Frameworks/Tk.framework/Versions/8.5/Tk']
EXPECTED_SHARED_LIBS = {}

# List of names of third party software built przy this installer.
# The names will be inserted into the rtf version of the License.
THIRD_PARTY_LIBS = []

# Instructions dla building libraries that are necessary dla building a
# batteries included python.
#   [The recipes are defined here dla convenience but instantiated later after
#    command line options have been processed.]
def library_recipes():
    result = []

    LT_10_5 = bool(getDeptargetTuple() < (10, 5))

    jeżeli getDeptargetTuple() < (10, 6):
        # The OpenSSL libs shipped przy OS X 10.5 oraz earlier are
        # hopelessly out-of-date oraz do nie include Apple's tie-in to
        # the root certificates w the user oraz system keychains via TEA
        # that was introduced w OS X 10.6.  Note that this applies to
        # programs built oraz linked przy a 10.5 SDK even when run on
        # newer versions of OS X.
        #
        # Dealing przy CAs jest messy.  For now, just supply a
        # local libssl oraz libcrypto dla the older installer variants
        # (e.g. the python.org 10.5+ 32-bit-only installer) that use the
        # same default ssl certfile location jako the system libs do:
        #   /System/Library/OpenSSL/cert.pem
        # Then at least TLS connections can be negotiated przy sites that
        # use sha-256 certs like python.org, assuming the proper CA certs
        # have been supplied.  The default CA cert management issues for
        # 10.5 oraz earlier builds are the same jako before, other than it jest
        # now more obvious przy cert checking enabled by default w the
        # standard library.
        #
        # For builds przy 10.6+ SDKs, continue to use the deprecated but
        # less out-of-date Apple 0.9.8 libs dla now.  While they are less
        # secure than using an up-to-date 1.0.1 version, doing so
        # avoids the big problems of forcing users to have to manage
        # default CAs themselves, thanks to the Apple libs using private TEA
        # APIs dla cert validation z keychains jeżeli validation using the
        # standard OpenSSL locations (/System/Library/OpenSSL, normally empty)
        # fails.

        result.extend([
          dict(
              name="OpenSSL 1.0.2d",
              url="https://www.openssl.org/source/openssl-1.0.2d.tar.gz",
              checksum='38dd619b2e77cbac69b99f52a053d25a',
              patches=[
                  "openssl_sdk_makedepend.patch",
                   ],
              buildrecipe=build_universal_openssl,
              configure=Nic,
              install=Nic,
          ),
        ])

#   Disable dla now
    jeżeli Nieprawda:   # jeżeli getDeptargetTuple() > (10, 5):
        result.extend([
          dict(
              name="Tcl 8.5.15",
              url="ftp://ftp.tcl.tk/pub/tcl//tcl8_5/tcl8.5.15-src.tar.gz",
              checksum='f3df162f92c69b254079c4d0af7a690f',
              buildDir="unix",
              configure_pre=[
                    '--enable-shared',
                    '--enable-threads',
                    '--libdir=/Library/Frameworks/Python.framework/Versions/%s/lib'%(getVersion(),),
              ],
              useLDFlags=Nieprawda,
              install='make TCL_LIBRARY=%(TCL_LIBRARY)s && make install TCL_LIBRARY=%(TCL_LIBRARY)s DESTDIR=%(DESTDIR)s'%{
                  "DESTDIR": shellQuote(os.path.join(WORKDIR, 'libraries')),
                  "TCL_LIBRARY": shellQuote('/Library/Frameworks/Python.framework/Versions/%s/lib/tcl8.5'%(getVersion())),
                  },
              ),
          dict(
              name="Tk 8.5.15",
              url="ftp://ftp.tcl.tk/pub/tcl//tcl8_5/tk8.5.15-src.tar.gz",
              checksum='55b8e33f903210a4e1c8bce0f820657f',
              patches=[
                  "issue19373_tk_8_5_15_source.patch",
                   ],
              buildDir="unix",
              configure_pre=[
                    '--enable-aqua',
                    '--enable-shared',
                    '--enable-threads',
                    '--libdir=/Library/Frameworks/Python.framework/Versions/%s/lib'%(getVersion(),),
              ],
              useLDFlags=Nieprawda,
              install='make TCL_LIBRARY=%(TCL_LIBRARY)s TK_LIBRARY=%(TK_LIBRARY)s && make install TCL_LIBRARY=%(TCL_LIBRARY)s TK_LIBRARY=%(TK_LIBRARY)s DESTDIR=%(DESTDIR)s'%{
                  "DESTDIR": shellQuote(os.path.join(WORKDIR, 'libraries')),
                  "TCL_LIBRARY": shellQuote('/Library/Frameworks/Python.framework/Versions/%s/lib/tcl8.5'%(getVersion())),
                  "TK_LIBRARY": shellQuote('/Library/Frameworks/Python.framework/Versions/%s/lib/tk8.5'%(getVersion())),
                  },
                ),
        ])

    jeżeli PYTHON_3:
        result.extend([
          dict(
              name="XZ 5.0.5",
              url="http://tukaani.org/xz/xz-5.0.5.tar.gz",
              checksum='19d924e066b6fff0bc9d1981b4e53196',
              configure_pre=[
                    '--disable-dependency-tracking',
              ]
              ),
        ])

    result.extend([
          dict(
              name="NCurses 5.9",
              url="http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz",
              checksum='8cb9c412e5f2d96bc6f459aa8c6282a1',
              configure_pre=[
                  "--enable-widec",
                  "--without-cxx",
                  "--without-cxx-binding",
                  "--without-ada",
                  "--without-curses-h",
                  "--enable-shared",
                  "--with-shared",
                  "--without-debug",
                  "--without-normal",
                  "--without-tests",
                  "--without-manpages",
                  "--datadir=/usr/share",
                  "--sysconfdir=/etc",
                  "--sharedstatedir=/usr/com",
                  "--with-terminfo-dirs=/usr/share/terminfo",
                  "--with-default-terminfo-dir=/usr/share/terminfo",
                  "--libdir=/Library/Frameworks/Python.framework/Versions/%s/lib"%(getVersion(),),
              ],
              patchscripts=[
                  ("ftp://invisible-island.net/ncurses//5.9/ncurses-5.9-20120616-patch.sh.bz2",
                   "f54bf02a349f96a7c4f0d00922f3a0d4"),
                   ],
              useLDFlags=Nieprawda,
              install='make && make install DESTDIR=%s && cd %s/usr/local/lib && ln -fs ../../../Library/Frameworks/Python.framework/Versions/%s/lib/lib* .'%(
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  getVersion(),
                  ),
          ),
          dict(
              name="SQLite 3.8.11",
              url="https://www.sqlite.org/2015/sqlite-autoconf-3081100.tar.gz",
              checksum='77b451925121028befbddbf45ea2bc49',
              extra_cflags=('-Os '
                            '-DSQLITE_ENABLE_FTS4 '
                            '-DSQLITE_ENABLE_FTS3_PARENTHESIS '
                            '-DSQLITE_ENABLE_RTREE '
                            '-DSQLITE_TCL=0 '
                 '%s' % ('','-DSQLITE_WITHOUT_ZONEMALLOC ')[LT_10_5]),
              configure_pre=[
                  '--enable-threadsafe',
                  '--enable-shared=no',
                  '--enable-static=yes',
                  '--disable-readline',
                  '--disable-dependency-tracking',
              ]
          ),
        ])

    jeżeli getDeptargetTuple() < (10, 5):
        result.extend([
          dict(
              name="Bzip2 1.0.6",
              url="http://bzip.org/1.0.6/bzip2-1.0.6.tar.gz",
              checksum='00b516f4704d4a7cb50a1d97e6e8e15b',
              configure=Nic,
              install='make install CC=%s CXX=%s, PREFIX=%s/usr/local/ CFLAGS="-arch %s -isysroot %s"'%(
                  CC, CXX,
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  ' -arch '.join(ARCHLIST),
                  SDKPATH,
              ),
          ),
          dict(
              name="ZLib 1.2.3",
              url="http://www.gzip.org/zlib/zlib-1.2.3.tar.gz",
              checksum='debc62758716a169df9f62e6ab2bc634',
              configure=Nic,
              install='make install CC=%s CXX=%s, prefix=%s/usr/local/ CFLAGS="-arch %s -isysroot %s"'%(
                  CC, CXX,
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  ' -arch '.join(ARCHLIST),
                  SDKPATH,
              ),
          ),
          dict(
              # Note that GNU readline jest GPL'd software
              name="GNU Readline 6.1.2",
              url="http://ftp.gnu.org/pub/gnu/readline/readline-6.1.tar.gz" ,
              checksum='fc2f7e714fe792db1ce6ddc4c9fb4ef3',
              patchlevel='0',
              patches=[
                  # The readline maintainers don't do actual micro releases, but
                  # just ship a set of patches.
                  ('http://ftp.gnu.org/pub/gnu/readline/readline-6.1-patches/readline61-001',
                   'c642f2e84d820884b0bf9fd176bc6c3f'),
                  ('http://ftp.gnu.org/pub/gnu/readline/readline-6.1-patches/readline61-002',
                   '1a76781a1ea734e831588285db7ec9b1'),
              ]
          ),
        ])

    jeżeli nie PYTHON_3:
        result.extend([
          dict(
              name="Sleepycat DB 4.7.25",
              url="http://download.oracle.com/berkeley-db/db-4.7.25.tar.gz",
              checksum='ec2b87e833779681a0c3a814aa71359e',
              buildDir="build_unix",
              configure="../dist/configure",
              configure_pre=[
                  '--includedir=/usr/local/include/db4',
              ]
          ),
        ])

    zwróć result


# Instructions dla building packages inside the .mpkg.
def pkg_recipes():
    unselected_for_python3 = ('selected', 'unselected')[PYTHON_3]
    result = [
        dict(
            name="PythonFramework",
            long_name="Python Framework",
            source="/Library/Frameworks/Python.framework",
            readme="""\
                This package installs Python.framework, that jest the python
                interpreter oraz the standard library. This also includes Python
                wrappers dla lots of Mac OS X API's.
            """,
            postflight="scripts/postflight.framework",
            selected='selected',
        ),
        dict(
            name="PythonApplications",
            long_name="GUI Applications",
            source="/Applications/Python %(VER)s",
            readme="""\
                This package installs IDLE (an interactive Python IDE),
                Python Launcher oraz Build Applet (create application bundles
                z python scripts).

                It also installs a number of examples oraz demos.
                """,
            required=Nieprawda,
            selected='selected',
        ),
        dict(
            name="PythonUnixTools",
            long_name="UNIX command-line tools",
            source="/usr/local/bin",
            readme="""\
                This package installs the unix tools w /usr/local/bin for
                compatibility przy older releases of Python. This package
                jest nie necessary to use Python.
                """,
            required=Nieprawda,
            selected='selected',
        ),
        dict(
            name="PythonDocumentation",
            long_name="Python Documentation",
            topdir="/Library/Frameworks/Python.framework/Versions/%(VER)s/Resources/English.lproj/Documentation",
            source="/pydocs",
            readme="""\
                This package installs the python documentation at a location
                that jest useable dla pydoc oraz IDLE.
                """,
            postflight="scripts/postflight.documentation",
            required=Nieprawda,
            selected='selected',
        ),
        dict(
            name="PythonProfileChanges",
            long_name="Shell profile updater",
            readme="""\
                This packages updates your shell profile to make sure that
                the Python tools are found by your shell w preference of
                the system provided Python tools.

                If you don't install this package you'll have to add
                "/Library/Frameworks/Python.framework/Versions/%(VER)s/bin"
                to your PATH by hand.
                """,
            postflight="scripts/postflight.patch-profile",
            topdir="/Library/Frameworks/Python.framework",
            source="/empty-dir",
            required=Nieprawda,
            selected='selected',
        ),
        dict(
            name="PythonInstallPip",
            long_name="Install albo upgrade pip",
            readme="""\
                This package installs (or upgrades z an earlier version)
                pip, a tool dla installing oraz managing Python packages.
                """,
            postflight="scripts/postflight.ensurepip",
            topdir="/Library/Frameworks/Python.framework",
            source="/empty-dir",
            required=Nieprawda,
            selected='selected',
        ),
    ]

    jeżeli getDeptargetTuple() < (10, 4) oraz nie PYTHON_3:
        result.append(
            dict(
                name="PythonSystemFixes",
                long_name="Fix system Python",
                readme="""\
                    This package updates the system python installation on
                    Mac OS X 10.3 to ensure that you can build new python extensions
                    using that copy of python after installing this version.
                    """,
                postflight="../Tools/fixapplepython23.py",
                topdir="/Library/Frameworks/Python.framework",
                source="/empty-dir",
                required=Nieprawda,
                selected=unselected_for_python3,
            )
        )

    zwróć result

def fatal(msg):
    """
    A fatal error, bail out.
    """
    sys.stderr.write('FATAL: ')
    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.exit(1)

def fileContents(fn):
    """
    Return the contents of the named file
    """
    zwróć open(fn, 'r').read()

def runCommand(commandline):
    """
    Run a command oraz podnieś RuntimeError jeżeli it fails. Output jest suppressed
    unless the command fails.
    """
    fd = os.popen(commandline, 'r')
    data = fd.read()
    xit = fd.close()
    jeżeli xit jest nie Nic:
        sys.stdout.write(data)
        podnieś RuntimeError("command failed: %s"%(commandline,))

    jeżeli VERBOSE:
        sys.stdout.write(data); sys.stdout.flush()

def captureCommand(commandline):
    fd = os.popen(commandline, 'r')
    data = fd.read()
    xit = fd.close()
    jeżeli xit jest nie Nic:
        sys.stdout.write(data)
        podnieś RuntimeError("command failed: %s"%(commandline,))

    zwróć data

def getTclTkVersion(configfile, versionline):
    """
    search Tcl albo Tk configuration file dla version line
    """
    spróbuj:
        f = open(configfile, "r")
    wyjąwszy OSError:
        fatal("Framework configuration file nie found: %s" % configfile)

    dla l w f:
        jeżeli l.startswith(versionline):
            f.close()
            zwróć l

    fatal("Version variable %s nie found w framework configuration file: %s"
            % (versionline, configfile))

def checkEnvironment():
    """
    Check that we're running on a supported system.
    """

    jeżeli sys.version_info[0:2] < (2, 4):
        fatal("This script must be run przy Python 2.4 albo later")

    jeżeli platform.system() != 'Darwin':
        fatal("This script should be run on a Mac OS X 10.4 (or later) system")

    jeżeli int(platform.release().split('.')[0]) < 8:
        fatal("This script should be run on a Mac OS X 10.4 (or later) system")

    jeżeli nie os.path.exists(SDKPATH):
        fatal("Please install the latest version of Xcode oraz the %s SDK"%(
            os.path.basename(SDKPATH[:-4])))

    # Because we only support dynamic load of only one major/minor version of
    # Tcl/Tk, ensure:
    # 1. there are no user-installed frameworks of Tcl/Tk przy version
    #       higher than the Apple-supplied system version w
    #       SDKROOT/System/Library/Frameworks
    # 2. there jest a user-installed framework (usually ActiveTcl) w (or linked
    #       in) SDKROOT/Library/Frameworks przy the same version jako the system
    #       version. This allows users to choose to install a newer patch level.

    frameworks = {}
    dla framework w ['Tcl', 'Tk']:
        fwpth = 'Library/Frameworks/%s.framework/Versions/Current' % framework
        sysfw = os.path.join(SDKPATH, 'System', fwpth)
        libfw = os.path.join(SDKPATH, fwpth)
        usrfw = os.path.join(os.getenv('HOME'), fwpth)
        frameworks[framework] = os.readlink(sysfw)
        jeżeli nie os.path.exists(libfw):
            fatal("Please install a link to a current %s %s jako %s so "
                    "the user can override the system framework."
                    % (framework, frameworks[framework], libfw))
        jeżeli os.readlink(libfw) != os.readlink(sysfw):
            fatal("Version of %s must match %s" % (libfw, sysfw) )
        jeżeli os.path.exists(usrfw):
            fatal("Please rename %s to avoid possible dynamic load issues."
                    % usrfw)

    jeżeli frameworks['Tcl'] != frameworks['Tk']:
        fatal("The Tcl oraz Tk frameworks are nie the same version.")

    # add files to check after build
    EXPECTED_SHARED_LIBS['_tkinter.so'] = [
            "/Library/Frameworks/Tcl.framework/Versions/%s/Tcl"
                % frameworks['Tcl'],
            "/Library/Frameworks/Tk.framework/Versions/%s/Tk"
                % frameworks['Tk'],
            ]

    # Remove inherited environment variables which might influence build
    environ_var_prefixes = ['CPATH', 'C_INCLUDE_', 'DYLD_', 'LANG', 'LC_',
                            'LD_', 'LIBRARY_', 'PATH', 'PYTHON']
    dla ev w list(os.environ):
        dla prefix w environ_var_prefixes:
            jeżeli ev.startswith(prefix) :
                print("INFO: deleting environment variable %s=%s" % (
                                                    ev, os.environ[ev]))
                usuń os.environ[ev]

    base_path = '/bin:/sbin:/usr/bin:/usr/sbin'
    jeżeli 'SDK_TOOLS_BIN' w os.environ:
        base_path = os.environ['SDK_TOOLS_BIN'] + ':' + base_path
    # Xcode 2.5 on OS X 10.4 does nie include SetFile w its usr/bin;
    # add its fixed location here jeżeli it exists
    OLD_DEVELOPER_TOOLS = '/Developer/Tools'
    jeżeli os.path.isdir(OLD_DEVELOPER_TOOLS):
        base_path = base_path + ':' + OLD_DEVELOPER_TOOLS
    os.environ['PATH'] = base_path
    print("Setting default PATH: %s"%(os.environ['PATH']))
    # Ensure ws have access to hg oraz to sphinx-build.
    # You may have to create links w /usr/bin dla them.
    runCommand('hg --version')
    runCommand('sphinx-build --version')

def parseOptions(args=Nic):
    """
    Parse arguments oraz update global settings.
    """
    global WORKDIR, DEPSRC, SDKPATH, SRCDIR, DEPTARGET
    global UNIVERSALOPTS, UNIVERSALARCHS, ARCHLIST, CC, CXX
    global FW_VERSION_PREFIX

    jeżeli args jest Nic:
        args = sys.argv[1:]

    spróbuj:
        options, args = getopt.getopt(args, '?hb',
                [ 'build-dir=', 'third-party=', 'sdk-path=' , 'src-dir=',
                  'dep-target=', 'universal-archs=', 'help' ])
    wyjąwszy getopt.GetoptError:
        print(sys.exc_info()[1])
        sys.exit(1)

    jeżeli args:
        print("Additional arguments")
        sys.exit(1)

    deptarget = Nic
    dla k, v w options:
        jeżeli k w ('-h', '-?', '--help'):
            print(USAGE)
            sys.exit(0)

        albo_inaczej k w ('-d', '--build-dir'):
            WORKDIR=v

        albo_inaczej k w ('--third-party',):
            DEPSRC=v

        albo_inaczej k w ('--sdk-path',):
            SDKPATH=v

        albo_inaczej k w ('--src-dir',):
            SRCDIR=v

        albo_inaczej k w ('--dep-target', ):
            DEPTARGET=v
            deptarget=v

        albo_inaczej k w ('--universal-archs', ):
            jeżeli v w UNIVERSALOPTS:
                UNIVERSALARCHS = v
                ARCHLIST = universal_opts_map[UNIVERSALARCHS]
                jeżeli deptarget jest Nic:
                    # Select alternate default deployment
                    # target
                    DEPTARGET = default_target_map.get(v, '10.3')
            inaczej:
                podnieś NotImplementedError(v)

        inaczej:
            podnieś NotImplementedError(k)

    SRCDIR=os.path.abspath(SRCDIR)
    WORKDIR=os.path.abspath(WORKDIR)
    SDKPATH=os.path.abspath(SDKPATH)
    DEPSRC=os.path.abspath(DEPSRC)

    CC, CXX = getTargetCompilers()

    FW_VERSION_PREFIX = FW_PREFIX[:] + ["Versions", getVersion()]

    print("-- Settings:")
    print("   * Source directory:    %s" % SRCDIR)
    print("   * Build directory:     %s" % WORKDIR)
    print("   * SDK location:        %s" % SDKPATH)
    print("   * Third-party source:  %s" % DEPSRC)
    print("   * Deployment target:   %s" % DEPTARGET)
    print("   * Universal archs:     %s" % str(ARCHLIST))
    print("   * C compiler:          %s" % CC)
    print("   * C++ compiler:        %s" % CXX)
    print("")
    print(" -- Building a Python %s framework at patch level %s"
                % (getVersion(), getFullVersion()))
    print("")

def extractArchive(builddir, archiveName):
    """
    Extract a source archive into 'builddir'. Returns the path of the
    extracted archive.

    XXX: This function assumes that archives contain a toplevel directory
    that jest has the same name jako the basename of the archive. This jest
    safe enough dla almost anything we use.  Unfortunately, it does nie
    work dla current Tcl oraz Tk source releases where the basename of
    the archive ends przy "-src" but the uncompressed directory does not.
    For now, just special case Tcl oraz Tk tar.gz downloads.
    """
    curdir = os.getcwd()
    spróbuj:
        os.chdir(builddir)
        jeżeli archiveName.endswith('.tar.gz'):
            retval = os.path.basename(archiveName[:-7])
            jeżeli ((retval.startswith('tcl') albo retval.startswith('tk'))
                    oraz retval.endswith('-src')):
                retval = retval[:-4]
            jeżeli os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("tar zxf %s 2>&1"%(shellQuote(archiveName),), 'r')

        albo_inaczej archiveName.endswith('.tar.bz2'):
            retval = os.path.basename(archiveName[:-8])
            jeżeli os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("tar jxf %s 2>&1"%(shellQuote(archiveName),), 'r')

        albo_inaczej archiveName.endswith('.tar'):
            retval = os.path.basename(archiveName[:-4])
            jeżeli os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("tar xf %s 2>&1"%(shellQuote(archiveName),), 'r')

        albo_inaczej archiveName.endswith('.zip'):
            retval = os.path.basename(archiveName[:-4])
            jeżeli os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("unzip %s 2>&1"%(shellQuote(archiveName),), 'r')

        data = fp.read()
        xit = fp.close()
        jeżeli xit jest nie Nic:
            sys.stdout.write(data)
            podnieś RuntimeError("Cannot extract %s"%(archiveName,))

        zwróć os.path.join(builddir, retval)

    w_końcu:
        os.chdir(curdir)

def downloadURL(url, fname):
    """
    Download the contents of the url into the file.
    """
    fpIn = urllib_request.urlopen(url)
    fpOut = open(fname, 'wb')
    block = fpIn.read(10240)
    spróbuj:
        dopóki block:
            fpOut.write(block)
            block = fpIn.read(10240)
        fpIn.close()
        fpOut.close()
    wyjąwszy:
        spróbuj:
            os.unlink(fname)
        wyjąwszy OSError:
            dalej

def verifyThirdPartyFile(url, checksum, fname):
    """
    Download file z url to filename fname jeżeli it does nie already exist.
    Abort jeżeli file contents does nie match supplied md5 checksum.
    """
    name = os.path.basename(fname)
    jeżeli os.path.exists(fname):
        print("Using local copy of %s"%(name,))
    inaczej:
        print("Did nie find local copy of %s"%(name,))
        print("Downloading %s"%(name,))
        downloadURL(url, fname)
        print("Archive dla %s stored jako %s"%(name, fname))
    jeżeli os.system(
            'MD5=$(openssl md5 %s) ; test "${MD5##*= }" = "%s"'
                % (shellQuote(fname), checksum) ):
        fatal('MD5 checksum mismatch dla file %s' % fname)

def build_universal_openssl(basedir, archList):
    """
    Special case build recipe dla universal build of openssl.

    The upstream OpenSSL build system does nie directly support
    OS X universal builds.  We need to build each architecture
    separately then lipo them together into fat libraries.
    """

    # OpenSSL fails to build przy Xcode 2.5 (on OS X 10.4).
    # If we are building on a 10.4.x albo earlier system,
    # unilaterally disable assembly code building to avoid the problem.
    no_asm = int(platform.release().split(".")[0]) < 9

    def build_openssl_arch(archbase, arch):
        "Build one architecture of openssl"
        arch_opts = {
            "i386": ["darwin-i386-cc"],
            "x86_64": ["darwin64-x86_64-cc", "enable-ec_nistp_64_gcc_128"],
            "ppc": ["darwin-ppc-cc"],
            "ppc64": ["darwin64-ppc-cc"],
        }
        configure_opts = [
            "no-krb5",
            "no-idea",
            "no-mdc2",
            "no-rc5",
            "no-zlib",
            "enable-tlsext",
            "no-ssl2",
            "no-ssl3",
            "no-ssl3-method",
            # "enable-unit-test",
            "shared",
            "--install_prefix=%s"%shellQuote(archbase),
            "--prefix=%s"%os.path.join("/", *FW_VERSION_PREFIX),
            "--openssldir=/System/Library/OpenSSL",
        ]
        jeżeli no_asm:
            configure_opts.append("no-asm")
        runCommand(" ".join(["perl", "Configure"]
                        + arch_opts[arch] + configure_opts))
        runCommand("make depend OSX_SDK=%s" % SDKPATH)
        runCommand("make all OSX_SDK=%s" % SDKPATH)
        runCommand("make install_sw OSX_SDK=%s" % SDKPATH)
        # runCommand("make test")
        zwróć

    srcdir = os.getcwd()
    universalbase = os.path.join(srcdir, "..",
                        os.path.basename(srcdir) + "-universal")
    os.mkdir(universalbase)
    archbasefws = []
    dla arch w archList:
        # fresh copy of the source tree
        archsrc = os.path.join(universalbase, arch, "src")
        shutil.copytree(srcdir, archsrc, symlinks=Prawda)
        # install base dla this arch
        archbase = os.path.join(universalbase, arch, "root")
        os.mkdir(archbase)
        # Python framework base within install_prefix:
        # the build will install into this framework..
        # This jest to ensure that the resulting shared libs have
        # the desired real install paths built into them.
        archbasefw = os.path.join(archbase, *FW_VERSION_PREFIX)

        # build one architecture
        os.chdir(archsrc)
        build_openssl_arch(archbase, arch)
        os.chdir(srcdir)
        archbasefws.append(archbasefw)

    # copy arch-independent files z last build into the basedir framework
    basefw = os.path.join(basedir, *FW_VERSION_PREFIX)
    shutil.copytree(
            os.path.join(archbasefw, "include", "openssl"),
            os.path.join(basefw, "include", "openssl")
            )

    shlib_version_number = grepValue(os.path.join(archsrc, "Makefile"),
            "SHLIB_VERSION_NUMBER")
    #   e.g. -> "1.0.0"
    libcrypto = "libcrypto.dylib"
    libcrypto_versioned = libcrypto.replace(".", "."+shlib_version_number+".")
    #   e.g. -> "libcrypto.1.0.0.dylib"
    libssl = "libssl.dylib"
    libssl_versioned = libssl.replace(".", "."+shlib_version_number+".")
    #   e.g. -> "libssl.1.0.0.dylib"

    spróbuj:
        os.mkdir(os.path.join(basefw, "lib"))
    wyjąwszy OSError:
        dalej

    # merge the individual arch-dependent shared libs into a fat shared lib
    archbasefws.insert(0, basefw)
    dla (lib_unversioned, lib_versioned) w [
                (libcrypto, libcrypto_versioned),
                (libssl, libssl_versioned)
            ]:
        runCommand("lipo -create -output " +
                    " ".join(shellQuote(
                            os.path.join(fw, "lib", lib_versioned))
                                    dla fw w archbasefws))
        # oraz create an unversioned symlink of it
        os.symlink(lib_versioned, os.path.join(basefw, "lib", lib_unversioned))

    # Create links w the temp include oraz lib dirs that will be injected
    # into the Python build so that setup.py can find them dopóki building
    # oraz the versioned links so that the setup.py post-build zaimportuj test
    # does nie fail.
    relative_path = os.path.join("..", "..", "..", *FW_VERSION_PREFIX)
    dla fn w [
            ["include", "openssl"],
            ["lib", libcrypto],
            ["lib", libssl],
            ["lib", libcrypto_versioned],
            ["lib", libssl_versioned],
        ]:
        os.symlink(
            os.path.join(relative_path, *fn),
            os.path.join(basedir, "usr", "local", *fn)
        )

    zwróć

def buildRecipe(recipe, basedir, archList):
    """
    Build software using a recipe. This function does the
    'configure;make;make install' dance dla C software, przy a possibility
    to customize this process, basically a poor-mans DarwinPorts.
    """
    curdir = os.getcwd()

    name = recipe['name']
    THIRD_PARTY_LIBS.append(name)
    url = recipe['url']
    configure = recipe.get('configure', './configure')
    buildrecipe = recipe.get('buildrecipe', Nic)
    install = recipe.get('install', 'make && make install DESTDIR=%s'%(
        shellQuote(basedir)))

    archiveName = os.path.split(url)[-1]
    sourceArchive = os.path.join(DEPSRC, archiveName)

    jeżeli nie os.path.exists(DEPSRC):
        os.mkdir(DEPSRC)

    verifyThirdPartyFile(url, recipe['checksum'], sourceArchive)
    print("Extracting archive dla %s"%(name,))
    buildDir=os.path.join(WORKDIR, '_bld')
    jeżeli nie os.path.exists(buildDir):
        os.mkdir(buildDir)

    workDir = extractArchive(buildDir, sourceArchive)
    os.chdir(workDir)

    dla patch w recipe.get('patches', ()):
        jeżeli isinstance(patch, tuple):
            url, checksum = patch
            fn = os.path.join(DEPSRC, os.path.basename(url))
            verifyThirdPartyFile(url, checksum, fn)
        inaczej:
            # patch jest a file w the source directory
            fn = os.path.join(curdir, patch)
        runCommand('patch -p%s < %s'%(recipe.get('patchlevel', 1),
            shellQuote(fn),))

    dla patchscript w recipe.get('patchscripts', ()):
        jeżeli isinstance(patchscript, tuple):
            url, checksum = patchscript
            fn = os.path.join(DEPSRC, os.path.basename(url))
            verifyThirdPartyFile(url, checksum, fn)
        inaczej:
            # patch jest a file w the source directory
            fn = os.path.join(curdir, patchscript)
        jeżeli fn.endswith('.bz2'):
            runCommand('bunzip2 -fk %s' % shellQuote(fn))
            fn = fn[:-4]
        runCommand('sh %s' % shellQuote(fn))
        os.unlink(fn)

    jeżeli 'buildDir' w recipe:
        os.chdir(recipe['buildDir'])

    jeżeli configure jest nie Nic:
        configure_args = [
            "--prefix=/usr/local",
            "--enable-static",
            "--disable-shared",
            #"CPP=gcc -arch %s -E"%(' -arch '.join(archList,),),
        ]

        jeżeli 'configure_pre' w recipe:
            args = list(recipe['configure_pre'])
            jeżeli '--disable-static' w args:
                configure_args.remove('--enable-static')
            jeżeli '--enable-shared' w args:
                configure_args.remove('--disable-shared')
            configure_args.extend(args)

        jeżeli recipe.get('useLDFlags', 1):
            configure_args.extend([
                "CFLAGS=%s-mmacosx-version-min=%s -arch %s -isysroot %s "
                            "-I%s/usr/local/include"%(
                        recipe.get('extra_cflags', ''),
                        DEPTARGET,
                        ' -arch '.join(archList),
                        shellQuote(SDKPATH)[1:-1],
                        shellQuote(basedir)[1:-1],),
                "LDFLAGS=-mmacosx-version-min=%s -isysroot %s -L%s/usr/local/lib -arch %s"%(
                    DEPTARGET,
                    shellQuote(SDKPATH)[1:-1],
                    shellQuote(basedir)[1:-1],
                    ' -arch '.join(archList)),
            ])
        inaczej:
            configure_args.extend([
                "CFLAGS=%s-mmacosx-version-min=%s -arch %s -isysroot %s "
                            "-I%s/usr/local/include"%(
                        recipe.get('extra_cflags', ''),
                        DEPTARGET,
                        ' -arch '.join(archList),
                        shellQuote(SDKPATH)[1:-1],
                        shellQuote(basedir)[1:-1],),
            ])

        jeżeli 'configure_post' w recipe:
            configure_args = configure_args + list(recipe['configure_post'])

        configure_args.insert(0, configure)
        configure_args = [ shellQuote(a) dla a w configure_args ]

        print("Running configure dla %s"%(name,))
        runCommand(' '.join(configure_args) + ' 2>&1')

    jeżeli buildrecipe jest nie Nic:
        # call special-case build recipe, e.g. dla openssl
        buildrecipe(basedir, archList)

    jeżeli install jest nie Nic:
        print("Running install dla %s"%(name,))
        runCommand('{ ' + install + ' ;} 2>&1')

    print("Done %s"%(name,))
    print("")

    os.chdir(curdir)

def buildLibraries():
    """
    Build our dependencies into $WORKDIR/libraries/usr/local
    """
    print("")
    print("Building required libraries")
    print("")
    universal = os.path.join(WORKDIR, 'libraries')
    os.mkdir(universal)
    os.makedirs(os.path.join(universal, 'usr', 'local', 'lib'))
    os.makedirs(os.path.join(universal, 'usr', 'local', 'include'))

    dla recipe w library_recipes():
        buildRecipe(recipe, universal, ARCHLIST)



def buildPythonDocs():
    # This stores the documentation jako Resources/English.lproj/Documentation
    # inside the framwork. pydoc oraz IDLE will pick it up there.
    print("Install python documentation")
    rootDir = os.path.join(WORKDIR, '_root')
    buildDir = os.path.join('../../Doc')
    docdir = os.path.join(rootDir, 'pydocs')
    curDir = os.getcwd()
    os.chdir(buildDir)
    # The Doc build changed dla 3.4 (technically, dla 3.4.1) oraz dla 2.7.9
    runCommand('make clean')
    # Assume sphinx-build jest on our PATH, checked w checkEnvironment
    runCommand('make html')
    os.chdir(curDir)
    jeżeli nie os.path.exists(docdir):
        os.mkdir(docdir)
    os.rename(os.path.join(buildDir, 'build', 'html'), docdir)


def buildPython():
    print("Building a universal python dla %s architectures" % UNIVERSALARCHS)

    buildDir = os.path.join(WORKDIR, '_bld', 'python')
    rootDir = os.path.join(WORKDIR, '_root')

    jeżeli os.path.exists(buildDir):
        shutil.rmtree(buildDir)
    jeżeli os.path.exists(rootDir):
        shutil.rmtree(rootDir)
    os.makedirs(buildDir)
    os.makedirs(rootDir)
    os.makedirs(os.path.join(rootDir, 'empty-dir'))
    curdir = os.getcwd()
    os.chdir(buildDir)

    # Not sure jeżeli this jest still needed, the original build script
    # claims that parts of the install assume python.exe exists.
    os.symlink('python', os.path.join(buildDir, 'python.exe'))

    # Extract the version z the configure file, needed to calculate
    # several paths.
    version = getVersion()

    # Since the extra libs are nie w their installed framework location
    # during the build, augment the library path so that the interpreter
    # will find them during its extension zaimportuj sanity checks.
    os.environ['DYLD_LIBRARY_PATH'] = os.path.join(WORKDIR,
                                        'libraries', 'usr', 'local', 'lib')
    print("Running configure...")
    runCommand("%s -C --enable-framework --enable-universalsdk=%s "
               "--with-universal-archs=%s "
               "%s "
               "%s "
               "LDFLAGS='-g -L%s/libraries/usr/local/lib' "
               "CFLAGS='-g -I%s/libraries/usr/local/include' 2>&1"%(
        shellQuote(os.path.join(SRCDIR, 'configure')), shellQuote(SDKPATH),
        UNIVERSALARCHS,
        (' ', '--with-computed-gotos ')[PYTHON_3],
        (' ', '--without-ensurepip ')[PYTHON_3],
        shellQuote(WORKDIR)[1:-1],
        shellQuote(WORKDIR)[1:-1]))

    print("Running make touch")
    runCommand("make touch")

    print("Running make")
    runCommand("make")

    print("Running make install")
    runCommand("make install DESTDIR=%s"%(
        shellQuote(rootDir)))

    print("Running make frameworkinstallextras")
    runCommand("make frameworkinstallextras DESTDIR=%s"%(
        shellQuote(rootDir)))

    usuń os.environ['DYLD_LIBRARY_PATH']
    print("Copying required shared libraries")
    jeżeli os.path.exists(os.path.join(WORKDIR, 'libraries', 'Library')):
        runCommand("mv %s/* %s"%(
            shellQuote(os.path.join(
                WORKDIR, 'libraries', 'Library', 'Frameworks',
                'Python.framework', 'Versions', getVersion(),
                'lib')),
            shellQuote(os.path.join(WORKDIR, '_root', 'Library', 'Frameworks',
                'Python.framework', 'Versions', getVersion(),
                'lib'))))

    path_to_lib = os.path.join(rootDir, 'Library', 'Frameworks',
                                'Python.framework', 'Versions',
                                version, 'lib', 'python%s'%(version,))

    print("Fix file modes")
    frmDir = os.path.join(rootDir, 'Library', 'Frameworks', 'Python.framework')
    gid = grp.getgrnam('admin').gr_gid

    shared_lib_error = Nieprawda
    dla dirpath, dirnames, filenames w os.walk(frmDir):
        dla dn w dirnames:
            os.chmod(os.path.join(dirpath, dn), STAT_0o775)
            os.chown(os.path.join(dirpath, dn), -1, gid)

        dla fn w filenames:
            jeżeli os.path.islink(fn):
                kontynuuj

            # "chmod g+w $fn"
            p = os.path.join(dirpath, fn)
            st = os.stat(p)
            os.chmod(p, stat.S_IMODE(st.st_mode) | stat.S_IWGRP)
            os.chown(p, -1, gid)

            jeżeli fn w EXPECTED_SHARED_LIBS:
                # check to see that this file was linked przy the
                # expected library path oraz version
                data = captureCommand("otool -L %s" % shellQuote(p))
                dla sl w EXPECTED_SHARED_LIBS[fn]:
                    jeżeli ("\t%s " % sl) nie w data:
                        print("Expected shared lib %s was nie linked przy %s"
                                % (sl, p))
                        shared_lib_error = Prawda

    jeżeli shared_lib_error:
        fatal("Unexpected shared library errors.")

    jeżeli PYTHON_3:
        LDVERSION=Nic
        VERSION=Nic
        ABIFLAGS=Nic

        fp = open(os.path.join(buildDir, 'Makefile'), 'r')
        dla ln w fp:
            jeżeli ln.startswith('VERSION='):
                VERSION=ln.split()[1]
            jeżeli ln.startswith('ABIFLAGS='):
                ABIFLAGS=ln.split()[1]
            jeżeli ln.startswith('LDVERSION='):
                LDVERSION=ln.split()[1]
        fp.close()

        LDVERSION = LDVERSION.replace('$(VERSION)', VERSION)
        LDVERSION = LDVERSION.replace('$(ABIFLAGS)', ABIFLAGS)
        config_suffix = '-' + LDVERSION
    inaczej:
        config_suffix = ''      # Python 2.x

    # We added some directories to the search path during the configure
    # phase. Remove those because those directories won't be there on
    # the end-users system. Also remove the directories z _sysconfigdata.py
    # (added w 3.3) jeżeli it exists.

    include_path = '-I%s/libraries/usr/local/include' % (WORKDIR,)
    lib_path = '-L%s/libraries/usr/local/lib' % (WORKDIR,)

    # fix Makefile
    path = os.path.join(path_to_lib, 'config' + config_suffix, 'Makefile')
    fp = open(path, 'r')
    data = fp.read()
    fp.close()

    dla p w (include_path, lib_path):
        data = data.replace(" " + p, '')
        data = data.replace(p + " ", '')

    fp = open(path, 'w')
    fp.write(data)
    fp.close()

    # fix _sysconfigdata jeżeli it exists
    #
    # TODO: make this more robust!  test_sysconfig_module of
    # distutils.tests.test_sysconfig.SysconfigTestCase tests that
    # the output z get_config_var w both sysconfig oraz
    # distutils.sysconfig jest exactly the same dla both CFLAGS oraz
    # LDFLAGS.  The fixing up jest now complicated by the pretty
    # printing w _sysconfigdata.py.  Also, we are using the
    # pprint z the Python running the installer build which
    # may nie cosmetically format the same jako the pprint w the Python
    # being built (and which jest used to originally generate
    # _sysconfigdata.py).

    zaimportuj pprint
    path = os.path.join(path_to_lib, '_sysconfigdata.py')
    jeżeli os.path.exists(path):
        fp = open(path, 'r')
        data = fp.read()
        fp.close()
        # create build_time_vars dict
        exec(data)
        vars = {}
        dla k, v w build_time_vars.items():
            jeżeli type(v) == type(''):
                dla p w (include_path, lib_path):
                    v = v.replace(' ' + p, '')
                    v = v.replace(p + ' ', '')
            vars[k] = v

        fp = open(path, 'w')
        # duplicated z sysconfig._generate_posix_vars()
        fp.write('# system configuration generated oraz used by'
                    ' the sysconfig module\n')
        fp.write('build_time_vars = ')
        pprint.pprint(vars, stream=fp)
        fp.close()

    # Add symlinks w /usr/local/bin, using relative links
    usr_local_bin = os.path.join(rootDir, 'usr', 'local', 'bin')
    to_framework = os.path.join('..', '..', '..', 'Library', 'Frameworks',
            'Python.framework', 'Versions', version, 'bin')
    jeżeli os.path.exists(usr_local_bin):
        shutil.rmtree(usr_local_bin)
    os.makedirs(usr_local_bin)
    dla fn w os.listdir(
                os.path.join(frmDir, 'Versions', version, 'bin')):
        os.symlink(os.path.join(to_framework, fn),
                   os.path.join(usr_local_bin, fn))

    os.chdir(curdir)

    jeżeli PYTHON_3:
        # Remove the 'Current' link, that way we don't accidentally mess
        # przy an already installed version of python 2
        os.unlink(os.path.join(rootDir, 'Library', 'Frameworks',
                            'Python.framework', 'Versions', 'Current'))

def patchFile(inPath, outPath):
    data = fileContents(inPath)
    data = data.replace('$FULL_VERSION', getFullVersion())
    data = data.replace('$VERSION', getVersion())
    data = data.replace('$MACOSX_DEPLOYMENT_TARGET', ''.join((DEPTARGET, ' albo later')))
    data = data.replace('$ARCHITECTURES', ", ".join(universal_opts_map[UNIVERSALARCHS]))
    data = data.replace('$INSTALL_SIZE', installSize())
    data = data.replace('$THIRD_PARTY_LIBS', "\\\n".join(THIRD_PARTY_LIBS))

    # This one jest nie handy jako a template variable
    data = data.replace('$PYTHONFRAMEWORKINSTALLDIR', '/Library/Frameworks/Python.framework')
    fp = open(outPath, 'w')
    fp.write(data)
    fp.close()

def patchScript(inPath, outPath):
    major, minor = getVersionMajorMinor()
    data = fileContents(inPath)
    data = data.replace('@PYMAJOR@', str(major))
    data = data.replace('@PYVER@', getVersion())
    fp = open(outPath, 'w')
    fp.write(data)
    fp.close()
    os.chmod(outPath, STAT_0o755)



def packageFromRecipe(targetDir, recipe):
    curdir = os.getcwd()
    spróbuj:
        # The major version (such jako 2.5) jest included w the package name
        # because having two version of python installed at the same time jest
        # common.
        pkgname = '%s-%s'%(recipe['name'], getVersion())
        srcdir  = recipe.get('source')
        pkgroot = recipe.get('topdir', srcdir)
        postflight = recipe.get('postflight')
        readme = textwrap.dedent(recipe['readme'])
        isRequired = recipe.get('required', Prawda)

        print("- building package %s"%(pkgname,))

        # Substitute some variables
        textvars = dict(
            VER=getVersion(),
            FULLVER=getFullVersion(),
        )
        readme = readme % textvars

        jeżeli pkgroot jest nie Nic:
            pkgroot = pkgroot % textvars
        inaczej:
            pkgroot = '/'

        jeżeli srcdir jest nie Nic:
            srcdir = os.path.join(WORKDIR, '_root', srcdir[1:])
            srcdir = srcdir % textvars

        jeżeli postflight jest nie Nic:
            postflight = os.path.abspath(postflight)

        packageContents = os.path.join(targetDir, pkgname + '.pkg', 'Contents')
        os.makedirs(packageContents)

        jeżeli srcdir jest nie Nic:
            os.chdir(srcdir)
            runCommand("pax -wf %s . 2>&1"%(shellQuote(os.path.join(packageContents, 'Archive.pax')),))
            runCommand("gzip -9 %s 2>&1"%(shellQuote(os.path.join(packageContents, 'Archive.pax')),))
            runCommand("mkbom . %s 2>&1"%(shellQuote(os.path.join(packageContents, 'Archive.bom')),))

        fn = os.path.join(packageContents, 'PkgInfo')
        fp = open(fn, 'w')
        fp.write('pmkrpkg1')
        fp.close()

        rsrcDir = os.path.join(packageContents, "Resources")
        os.mkdir(rsrcDir)
        fp = open(os.path.join(rsrcDir, 'ReadMe.txt'), 'w')
        fp.write(readme)
        fp.close()

        jeżeli postflight jest nie Nic:
            patchScript(postflight, os.path.join(rsrcDir, 'postflight'))

        vers = getFullVersion()
        major, minor = getVersionMajorMinor()
        pl = Plist(
                CFBundleGetInfoString="Python.%s %s"%(pkgname, vers,),
                CFBundleIdentifier='org.python.Python.%s'%(pkgname,),
                CFBundleName='Python.%s'%(pkgname,),
                CFBundleShortVersionString=vers,
                IFMajorVersion=major,
                IFMinorVersion=minor,
                IFPkgFormatVersion=0.10000000149011612,
                IFPkgFlagAllowBackRev=Nieprawda,
                IFPkgFlagAuthorizationAction="RootAuthorization",
                IFPkgFlagDefaultLocation=pkgroot,
                IFPkgFlagFollowLinks=Prawda,
                IFPkgFlagInstallFat=Prawda,
                IFPkgFlagIsRequired=isRequired,
                IFPkgFlagOverwritePermissions=Nieprawda,
                IFPkgFlagRelocatable=Nieprawda,
                IFPkgFlagRestartAction="NoRestart",
                IFPkgFlagRootVolumeOnly=Prawda,
                IFPkgFlagUpdateInstalledLangauges=Nieprawda,
            )
        writePlist(pl, os.path.join(packageContents, 'Info.plist'))

        pl = Plist(
                    IFPkgDescriptionDescription=readme,
                    IFPkgDescriptionTitle=recipe.get('long_name', "Python.%s"%(pkgname,)),
                    IFPkgDescriptionVersion=vers,
                )
        writePlist(pl, os.path.join(packageContents, 'Resources', 'Description.plist'))

    w_końcu:
        os.chdir(curdir)


def makeMpkgPlist(path):

    vers = getFullVersion()
    major, minor = getVersionMajorMinor()

    pl = Plist(
            CFBundleGetInfoString="Python %s"%(vers,),
            CFBundleIdentifier='org.python.Python',
            CFBundleName='Python',
            CFBundleShortVersionString=vers,
            IFMajorVersion=major,
            IFMinorVersion=minor,
            IFPkgFlagComponentDirectory="Contents/Packages",
            IFPkgFlagPackageList=[
                dict(
                    IFPkgFlagPackageLocation='%s-%s.pkg'%(item['name'], getVersion()),
                    IFPkgFlagPackageSelection=item.get('selected', 'selected'),
                )
                dla item w pkg_recipes()
            ],
            IFPkgFormatVersion=0.10000000149011612,
            IFPkgFlagBackgroundScaling="proportional",
            IFPkgFlagBackgroundAlignment="left",
            IFPkgFlagAuthorizationAction="RootAuthorization",
        )

    writePlist(pl, path)


def buildInstaller():

    # Zap all compiled files
    dla dirpath, _, filenames w os.walk(os.path.join(WORKDIR, '_root')):
        dla fn w filenames:
            jeżeli fn.endswith('.pyc') albo fn.endswith('.pyo'):
                os.unlink(os.path.join(dirpath, fn))

    outdir = os.path.join(WORKDIR, 'installer')
    jeżeli os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

    pkgroot = os.path.join(outdir, 'Python.mpkg', 'Contents')
    pkgcontents = os.path.join(pkgroot, 'Packages')
    os.makedirs(pkgcontents)
    dla recipe w pkg_recipes():
        packageFromRecipe(pkgcontents, recipe)

    rsrcDir = os.path.join(pkgroot, 'Resources')

    fn = os.path.join(pkgroot, 'PkgInfo')
    fp = open(fn, 'w')
    fp.write('pmkrpkg1')
    fp.close()

    os.mkdir(rsrcDir)

    makeMpkgPlist(os.path.join(pkgroot, 'Info.plist'))
    pl = Plist(
                IFPkgDescriptionTitle="Python",
                IFPkgDescriptionVersion=getVersion(),
            )

    writePlist(pl, os.path.join(pkgroot, 'Resources', 'Description.plist'))
    dla fn w os.listdir('resources'):
        jeżeli fn == '.svn': kontynuuj
        jeżeli fn.endswith('.jpg'):
            shutil.copy(os.path.join('resources', fn), os.path.join(rsrcDir, fn))
        inaczej:
            patchFile(os.path.join('resources', fn), os.path.join(rsrcDir, fn))


def installSize(clear=Nieprawda, _saved=[]):
    jeżeli clear:
        usuń _saved[:]
    jeżeli nie _saved:
        data = captureCommand("du -ks %s"%(
                    shellQuote(os.path.join(WORKDIR, '_root'))))
        _saved.append("%d"%((0.5 + (int(data.split()[0]) / 1024.0)),))
    zwróć _saved[0]


def buildDMG():
    """
    Create DMG containing the rootDir.
    """
    outdir = os.path.join(WORKDIR, 'diskimage')
    jeżeli os.path.exists(outdir):
        shutil.rmtree(outdir)

    imagepath = os.path.join(outdir,
                    'python-%s-macosx%s'%(getFullVersion(),DEPTARGET))
    jeżeli INCLUDE_TIMESTAMP:
        imagepath = imagepath + '-%04d-%02d-%02d'%(time.localtime()[:3])
    imagepath = imagepath + '.dmg'

    os.mkdir(outdir)
    volname='Python %s'%(getFullVersion())
    runCommand("hdiutil create -format UDRW -volname %s -srcfolder %s %s"%(
            shellQuote(volname),
            shellQuote(os.path.join(WORKDIR, 'installer')),
            shellQuote(imagepath + ".tmp.dmg" )))


    jeżeli nie os.path.exists(os.path.join(WORKDIR, "mnt")):
        os.mkdir(os.path.join(WORKDIR, "mnt"))
    runCommand("hdiutil attach %s -mountroot %s"%(
        shellQuote(imagepath + ".tmp.dmg"), shellQuote(os.path.join(WORKDIR, "mnt"))))

    # Custom icon dla the DMG, shown when the DMG jest mounted.
    shutil.copy("../Icons/Disk Image.icns",
            os.path.join(WORKDIR, "mnt", volname, ".VolumeIcon.icns"))
    runCommand("SetFile -a C %s/"%(
            shellQuote(os.path.join(WORKDIR, "mnt", volname)),))

    runCommand("hdiutil detach %s"%(shellQuote(os.path.join(WORKDIR, "mnt", volname))))

    setIcon(imagepath + ".tmp.dmg", "../Icons/Disk Image.icns")
    runCommand("hdiutil convert %s -format UDZO -o %s"%(
            shellQuote(imagepath + ".tmp.dmg"), shellQuote(imagepath)))
    setIcon(imagepath, "../Icons/Disk Image.icns")

    os.unlink(imagepath + ".tmp.dmg")

    zwróć imagepath


def setIcon(filePath, icnsPath):
    """
    Set the custom icon dla the specified file albo directory.
    """

    dirPath = os.path.normpath(os.path.dirname(__file__))
    toolPath = os.path.join(dirPath, "seticon.app/Contents/MacOS/seticon")
    jeżeli nie os.path.exists(toolPath) albo os.stat(toolPath).st_mtime < os.stat(dirPath + '/seticon.m').st_mtime:
        # NOTE: The tool jest created inside an .app bundle, otherwise it won't work due
        # to connections to the window server.
        appPath = os.path.join(dirPath, "seticon.app/Contents/MacOS")
        jeżeli nie os.path.exists(appPath):
            os.makedirs(appPath)
        runCommand("cc -o %s %s/seticon.m -framework Cocoa"%(
            shellQuote(toolPath), shellQuote(dirPath)))

    runCommand("%s %s %s"%(shellQuote(os.path.abspath(toolPath)), shellQuote(icnsPath),
        shellQuote(filePath)))

def main():
    # First parse options oraz check jeżeli we can perform our work
    parseOptions()
    checkEnvironment()

    os.environ['MACOSX_DEPLOYMENT_TARGET'] = DEPTARGET
    os.environ['CC'] = CC
    os.environ['CXX'] = CXX

    jeżeli os.path.exists(WORKDIR):
        shutil.rmtree(WORKDIR)
    os.mkdir(WORKDIR)

    os.environ['LC_ALL'] = 'C'

    # Then build third-party libraries such jako sleepycat DB4.
    buildLibraries()

    # Now build python itself
    buildPython()

    # And then build the documentation
    # Remove the Deployment Target z the shell
    # environment, it's no longer needed oraz
    # an unexpected build target can cause problems
    # when Sphinx oraz its dependencies need to
    # be (re-)installed.
    usuń os.environ['MACOSX_DEPLOYMENT_TARGET']
    buildPythonDocs()


    # Prepare the applications folder
    folder = os.path.join(WORKDIR, "_root", "Applications", "Python %s"%(
        getVersion(),))
    fn = os.path.join(folder, "License.rtf")
    patchFile("resources/License.rtf",  fn)
    fn = os.path.join(folder, "ReadMe.rtf")
    patchFile("resources/ReadMe.rtf",  fn)
    fn = os.path.join(folder, "Update Shell Profile.command")
    patchScript("scripts/postflight.patch-profile",  fn)
    os.chmod(folder, STAT_0o755)
    setIcon(folder, "../Icons/Python Folder.icns")

    # Create the installer
    buildInstaller()

    # And copy the readme into the directory containing the installer
    patchFile('resources/ReadMe.rtf',
                os.path.join(WORKDIR, 'installer', 'ReadMe.rtf'))

    # Ditto dla the license file.
    patchFile('resources/License.rtf',
                os.path.join(WORKDIR, 'installer', 'License.rtf'))

    fp = open(os.path.join(WORKDIR, 'installer', 'Build.txt'), 'w')
    fp.write("# BUILD INFO\n")
    fp.write("# Date: %s\n" % time.ctime())
    fp.write("# By: %s\n" % pwd.getpwuid(os.getuid()).pw_gecos)
    fp.close()

    # And copy it to a DMG
    buildDMG()

jeżeli __name__ == "__main__":
    main()
