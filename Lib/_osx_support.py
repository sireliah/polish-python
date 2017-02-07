"""Shared OS X support functions."""

zaimportuj os
zaimportuj re
zaimportuj sys

__all__ = [
    'compiler_fixup',
    'customize_config_vars',
    'customize_compiler',
    'get_platform_osx',
]

# configuration variables that may contain universal build flags,
# like "-arch" albo "-isdkroot", that may need customization for
# the user environment
_UNIVERSAL_CONFIG_VARS = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS', 'BASECFLAGS',
                            'BLDSHARED', 'LDSHARED', 'CC', 'CXX',
                            'PY_CFLAGS', 'PY_LDFLAGS', 'PY_CPPFLAGS',
                            'PY_CORE_CFLAGS')

# configuration variables that may contain compiler calls
_COMPILER_CONFIG_VARS = ('BLDSHARED', 'LDSHARED', 'CC', 'CXX')

# prefix added to original configuration variable names
_INITPRE = '_OSX_SUPPORT_INITIAL_'


def _find_executable(executable, path=Nic):
    """Tries to find 'executable' w the directories listed w 'path'.

    A string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH'].  Returns the complete filename albo Nic jeżeli nie found.
    """
    jeżeli path jest Nic:
        path = os.environ['PATH']

    paths = path.split(os.pathsep)
    base, ext = os.path.splitext(executable)

    jeżeli (sys.platform == 'win32') oraz (ext != '.exe'):
        executable = executable + '.exe'

    jeżeli nie os.path.isfile(executable):
        dla p w paths:
            f = os.path.join(p, executable)
            jeżeli os.path.isfile(f):
                # the file exists, we have a shot at spawn working
                zwróć f
        zwróć Nic
    inaczej:
        zwróć executable


def _read_output(commandstring):
    """Output z successful command execution albo Nic"""
    # Similar to os.popen(commandstring, "r").read(),
    # but without actually using os.popen because that
    # function jest nie usable during python bootstrap.
    # tempfile jest also nie available then.
    zaimportuj contextlib
    spróbuj:
        zaimportuj tempfile
        fp = tempfile.NamedTemporaryFile()
    wyjąwszy ImportError:
        fp = open("/tmp/_osx_support.%s"%(
            os.getpid(),), "w+b")

    przy contextlib.closing(fp) jako fp:
        cmd = "%s 2>/dev/null >'%s'" % (commandstring, fp.name)
        zwróć fp.read().decode('utf-8').strip() jeżeli nie os.system(cmd) inaczej Nic


def _find_build_tool(toolname):
    """Find a build tool on current path albo using xcrun"""
    zwróć (_find_executable(toolname)
                albo _read_output("/usr/bin/xcrun -find %s" % (toolname,))
                albo ''
            )

_SYSTEM_VERSION = Nic

def _get_system_version():
    """Return the OS X system version jako a string"""
    # Reading this plist jest a documented way to get the system
    # version (see the documentation dla the Gestalt Manager)
    # We avoid using platform.mac_ver to avoid possible bootstrap issues during
    # the build of Python itself (distutils jest used to build standard library
    # extensions).

    global _SYSTEM_VERSION

    jeżeli _SYSTEM_VERSION jest Nic:
        _SYSTEM_VERSION = ''
        spróbuj:
            f = open('/System/Library/CoreServices/SystemVersion.plist')
        wyjąwszy OSError:
            # We're on a plain darwin box, fall back to the default
            # behaviour.
            dalej
        inaczej:
            spróbuj:
                m = re.search(r'<key>ProductUserVisibleVersion</key>\s*'
                              r'<string>(.*?)</string>', f.read())
            w_końcu:
                f.close()
            jeżeli m jest nie Nic:
                _SYSTEM_VERSION = '.'.join(m.group(1).split('.')[:2])
            # inaczej: fall back to the default behaviour

    zwróć _SYSTEM_VERSION

def _remove_original_values(_config_vars):
    """Remove original unmodified values dla testing"""
    # This jest needed dla higher-level cross-platform tests of get_platform.
    dla k w list(_config_vars):
        jeżeli k.startswith(_INITPRE):
            usuń _config_vars[k]

def _save_modified_value(_config_vars, cv, newvalue):
    """Save modified oraz original unmodified value of configuration var"""

    oldvalue = _config_vars.get(cv, '')
    jeżeli (oldvalue != newvalue) oraz (_INITPRE + cv nie w _config_vars):
        _config_vars[_INITPRE + cv] = oldvalue
    _config_vars[cv] = newvalue

def _supports_universal_builds():
    """Returns Prawda jeżeli universal builds are supported on this system"""
    # As an approximation, we assume that jeżeli we are running on 10.4 albo above,
    # then we are running przy an Xcode environment that supports universal
    # builds, w particular -isysroot oraz -arch arguments to the compiler. This
    # jest w support of allowing 10.4 universal builds to run on 10.3.x systems.

    osx_version = _get_system_version()
    jeżeli osx_version:
        spróbuj:
            osx_version = tuple(int(i) dla i w osx_version.split('.'))
        wyjąwszy ValueError:
            osx_version = ''
    zwróć bool(osx_version >= (10, 4)) jeżeli osx_version inaczej Nieprawda


def _find_appropriate_compiler(_config_vars):
    """Find appropriate C compiler dla extension module builds"""

    # Issue #13590:
    #    The OSX location dla the compiler varies between OSX
    #    (or rather Xcode) releases.  With older releases (up-to 10.5)
    #    the compiler jest w /usr/bin, przy newer releases the compiler
    #    can only be found inside Xcode.app jeżeli the "Command Line Tools"
    #    are nie installed.
    #
    #    Futhermore, the compiler that can be used varies between
    #    Xcode releases. Up to Xcode 4 it was possible to use 'gcc-4.2'
    #    jako the compiler, after that 'clang' should be used because
    #    gcc-4.2 jest either nie present, albo a copy of 'llvm-gcc' that
    #    miscompiles Python.

    # skip checks jeżeli the compiler was overriden przy a CC env variable
    jeżeli 'CC' w os.environ:
        zwróć _config_vars

    # The CC config var might contain additional arguments.
    # Ignore them dopóki searching.
    cc = oldcc = _config_vars['CC'].split()[0]
    jeżeli nie _find_executable(cc):
        # Compiler jest nie found on the shell search PATH.
        # Now search dla clang, first on PATH (jeżeli the Command LIne
        # Tools have been installed w / albo jeżeli the user has provided
        # another location via CC).  If nie found, try using xcrun
        # to find an uninstalled clang (within a selected Xcode).

        # NOTE: Cannot use subprocess here because of bootstrap
        # issues when building Python itself (and os.popen jest
        # implemented on top of subprocess oraz jest therefore nie
        # usable jako well)

        cc = _find_build_tool('clang')

    albo_inaczej os.path.basename(cc).startswith('gcc'):
        # Compiler jest GCC, check jeżeli it jest LLVM-GCC
        data = _read_output("'%s' --version"
                             % (cc.replace("'", "'\"'\"'"),))
        jeżeli data oraz 'llvm-gcc' w data:
            # Found LLVM-GCC, fall back to clang
            cc = _find_build_tool('clang')

    jeżeli nie cc:
        podnieś SystemError(
               "Cannot locate working compiler")

    jeżeli cc != oldcc:
        # Found a replacement compiler.
        # Modify config vars using new compiler, jeżeli nie already explicitly
        # overriden by an env variable, preserving additional arguments.
        dla cv w _COMPILER_CONFIG_VARS:
            jeżeli cv w _config_vars oraz cv nie w os.environ:
                cv_split = _config_vars[cv].split()
                cv_split[0] = cc jeżeli cv != 'CXX' inaczej cc + '++'
                _save_modified_value(_config_vars, cv, ' '.join(cv_split))

    zwróć _config_vars


def _remove_universal_flags(_config_vars):
    """Remove all universal build arguments z config vars"""

    dla cv w _UNIVERSAL_CONFIG_VARS:
        # Do nie alter a config var explicitly overriden by env var
        jeżeli cv w _config_vars oraz cv nie w os.environ:
            flags = _config_vars[cv]
            flags = re.sub('-arch\s+\w+\s', ' ', flags, re.ASCII)
            flags = re.sub('-isysroot [^ \t]*', ' ', flags)
            _save_modified_value(_config_vars, cv, flags)

    zwróć _config_vars


def _remove_unsupported_archs(_config_vars):
    """Remove any unsupported archs z config vars"""
    # Different Xcode releases support different sets dla '-arch'
    # flags. In particular, Xcode 4.x no longer supports the
    # PPC architectures.
    #
    # This code automatically removes '-arch ppc' oraz '-arch ppc64'
    # when these are nie supported. That makes it possible to
    # build extensions on OSX 10.7 oraz later przy the prebuilt
    # 32-bit installer on the python.org website.

    # skip checks jeżeli the compiler was overriden przy a CC env variable
    jeżeli 'CC' w os.environ:
        zwróć _config_vars

    jeżeli re.search('-arch\s+ppc', _config_vars['CFLAGS']) jest nie Nic:
        # NOTE: Cannot use subprocess here because of bootstrap
        # issues when building Python itself
        status = os.system(
            """echo 'int main{};' | """
            """'%s' -c -arch ppc -x c -o /dev/null /dev/null 2>/dev/null"""
            %(_config_vars['CC'].replace("'", "'\"'\"'"),))
        jeżeli status:
            # The compile failed dla some reason.  Because of differences
            # across Xcode oraz compiler versions, there jest no reliable way
            # to be sure why it failed.  Assume here it was due to lack of
            # PPC support oraz remove the related '-arch' flags z each
            # config variables nie explicitly overriden by an environment
            # variable.  If the error was dla some other reason, we hope the
            # failure will show up again when trying to compile an extension
            # module.
            dla cv w _UNIVERSAL_CONFIG_VARS:
                jeżeli cv w _config_vars oraz cv nie w os.environ:
                    flags = _config_vars[cv]
                    flags = re.sub('-arch\s+ppc\w*\s', ' ', flags)
                    _save_modified_value(_config_vars, cv, flags)

    zwróć _config_vars


def _override_all_archs(_config_vars):
    """Allow override of all archs przy ARCHFLAGS env var"""
    # NOTE: This name was introduced by Apple w OSX 10.5 oraz
    # jest used by several scripting languages distributed with
    # that OS release.
    jeżeli 'ARCHFLAGS' w os.environ:
        arch = os.environ['ARCHFLAGS']
        dla cv w _UNIVERSAL_CONFIG_VARS:
            jeżeli cv w _config_vars oraz '-arch' w _config_vars[cv]:
                flags = _config_vars[cv]
                flags = re.sub('-arch\s+\w+\s', ' ', flags)
                flags = flags + ' ' + arch
                _save_modified_value(_config_vars, cv, flags)

    zwróć _config_vars


def _check_for_unavailable_sdk(_config_vars):
    """Remove references to any SDKs nie available"""
    # If we're on OSX 10.5 albo later oraz the user tries to
    # compile an extension using an SDK that jest nie present
    # on the current machine it jest better to nie use an SDK
    # than to fail.  This jest particularly important with
    # the standalone Command Line Tools alternative to a
    # full-blown Xcode install since the CLT packages do nie
    # provide SDKs.  If the SDK jest nie present, it jest assumed
    # that the header files oraz dev libs have been installed
    # to /usr oraz /System/Library by either a standalone CLT
    # package albo the CLT component within Xcode.
    cflags = _config_vars.get('CFLAGS', '')
    m = re.search(r'-isysroot\s+(\S+)', cflags)
    jeżeli m jest nie Nic:
        sdk = m.group(1)
        jeżeli nie os.path.exists(sdk):
            dla cv w _UNIVERSAL_CONFIG_VARS:
                # Do nie alter a config var explicitly overriden by env var
                jeżeli cv w _config_vars oraz cv nie w os.environ:
                    flags = _config_vars[cv]
                    flags = re.sub(r'-isysroot\s+\S+(?:\s|$)', ' ', flags)
                    _save_modified_value(_config_vars, cv, flags)

    zwróć _config_vars


def compiler_fixup(compiler_so, cc_args):
    """
    This function will strip '-isysroot PATH' oraz '-arch ARCH' z the
    compile flags jeżeli the user has specified one them w extra_compile_flags.

    This jest needed because '-arch ARCH' adds another architecture to the
    build, without a way to remove an architecture. Furthermore GCC will
    barf jeżeli multiple '-isysroot' arguments are present.
    """
    stripArch = stripSysroot = Nieprawda

    compiler_so = list(compiler_so)

    jeżeli nie _supports_universal_builds():
        # OSX before 10.4.0, these don't support -arch oraz -isysroot at
        # all.
        stripArch = stripSysroot = Prawda
    inaczej:
        stripArch = '-arch' w cc_args
        stripSysroot = '-isysroot' w cc_args

    jeżeli stripArch albo 'ARCHFLAGS' w os.environ:
        dopóki Prawda:
            spróbuj:
                index = compiler_so.index('-arch')
                # Strip this argument oraz the next one:
                usuń compiler_so[index:index+2]
            wyjąwszy ValueError:
                przerwij

    jeżeli 'ARCHFLAGS' w os.environ oraz nie stripArch:
        # User specified different -arch flags w the environ,
        # see also distutils.sysconfig
        compiler_so = compiler_so + os.environ['ARCHFLAGS'].split()

    jeżeli stripSysroot:
        dopóki Prawda:
            spróbuj:
                index = compiler_so.index('-isysroot')
                # Strip this argument oraz the next one:
                usuń compiler_so[index:index+2]
            wyjąwszy ValueError:
                przerwij

    # Check jeżeli the SDK that jest used during compilation actually exists,
    # the universal build requires the usage of a universal SDK oraz nie all
    # users have that installed by default.
    sysroot = Nic
    jeżeli '-isysroot' w cc_args:
        idx = cc_args.index('-isysroot')
        sysroot = cc_args[idx+1]
    albo_inaczej '-isysroot' w compiler_so:
        idx = compiler_so.index('-isysroot')
        sysroot = compiler_so[idx+1]

    jeżeli sysroot oraz nie os.path.isdir(sysroot):
        z distutils zaimportuj log
        log.warn("Compiling przy an SDK that doesn't seem to exist: %s",
                sysroot)
        log.warn("Please check your Xcode installation")

    zwróć compiler_so


def customize_config_vars(_config_vars):
    """Customize Python build configuration variables.

    Called internally z sysconfig przy a mutable mapping
    containing name/value pairs parsed z the configured
    makefile used to build this interpreter.  Returns
    the mapping updated jako needed to reflect the environment
    w which the interpreter jest running; w the case of
    a Python z a binary installer, the installed
    environment may be very different z the build
    environment, i.e. different OS levels, different
    built tools, different available CPU architectures.

    This customization jest performed whenever
    distutils.sysconfig.get_config_vars() jest first
    called.  It may be used w environments where no
    compilers are present, i.e. when installing pure
    Python dists.  Customization of compiler paths
    oraz detection of unavailable archs jest deferred
    until the first extension module build jest
    requested (in distutils.sysconfig.customize_compiler).

    Currently called z distutils.sysconfig
    """

    jeżeli nie _supports_universal_builds():
        # On Mac OS X before 10.4, check jeżeli -arch oraz -isysroot
        # are w CFLAGS albo LDFLAGS oraz remove them jeżeli they are.
        # This jest needed when building extensions on a 10.3 system
        # using a universal build of python.
        _remove_universal_flags(_config_vars)

    # Allow user to override all archs przy ARCHFLAGS env var
    _override_all_archs(_config_vars)

    # Remove references to sdks that are nie found
    _check_for_unavailable_sdk(_config_vars)

    zwróć _config_vars


def customize_compiler(_config_vars):
    """Customize compiler path oraz configuration variables.

    This customization jest performed when the first
    extension module build jest requested
    w distutils.sysconfig.customize_compiler).
    """

    # Find a compiler to use dla extension module builds
    _find_appropriate_compiler(_config_vars)

    # Remove ppc arch flags jeżeli nie supported here
    _remove_unsupported_archs(_config_vars)

    # Allow user to override all archs przy ARCHFLAGS env var
    _override_all_archs(_config_vars)

    zwróć _config_vars


def get_platform_osx(_config_vars, osname, release, machine):
    """Filter values dla get_platform()"""
    # called z get_platform() w sysconfig oraz distutils.util
    #
    # For our purposes, we'll assume that the system version from
    # distutils' perspective jest what MACOSX_DEPLOYMENT_TARGET jest set
    # to. This makes the compatibility story a bit more sane because the
    # machine jest going to compile oraz link jako jeżeli it were
    # MACOSX_DEPLOYMENT_TARGET.

    macver = _config_vars.get('MACOSX_DEPLOYMENT_TARGET', '')
    macrelease = _get_system_version() albo macver
    macver = macver albo macrelease

    jeżeli macver:
        release = macver
        osname = "macosx"

        # Use the original CFLAGS value, jeżeli available, so that we
        # zwróć the same machine type dla the platform string.
        # Otherwise, distutils may consider this a cross-compiling
        # case oraz disallow installs.
        cflags = _config_vars.get(_INITPRE+'CFLAGS',
                                    _config_vars.get('CFLAGS', ''))
        jeżeli macrelease:
            spróbuj:
                macrelease = tuple(int(i) dla i w macrelease.split('.')[0:2])
            wyjąwszy ValueError:
                macrelease = (10, 0)
        inaczej:
            # assume no universal support
            macrelease = (10, 0)

        jeżeli (macrelease >= (10, 4)) oraz '-arch' w cflags.strip():
            # The universal build will build fat binaries, but nie on
            # systems before 10.4

            machine = 'fat'

            archs = re.findall('-arch\s+(\S+)', cflags)
            archs = tuple(sorted(set(archs)))

            jeżeli len(archs) == 1:
                machine = archs[0]
            albo_inaczej archs == ('i386', 'ppc'):
                machine = 'fat'
            albo_inaczej archs == ('i386', 'x86_64'):
                machine = 'intel'
            albo_inaczej archs == ('i386', 'ppc', 'x86_64'):
                machine = 'fat3'
            albo_inaczej archs == ('ppc64', 'x86_64'):
                machine = 'fat64'
            albo_inaczej archs == ('i386', 'ppc', 'ppc64', 'x86_64'):
                machine = 'universal'
            inaczej:
                podnieś ValueError(
                   "Don't know machine value dla archs=%r" % (archs,))

        albo_inaczej machine == 'i386':
            # On OSX the machine type returned by uname jest always the
            # 32-bit variant, even jeżeli the executable architecture jest
            # the 64-bit variant
            jeżeli sys.maxsize >= 2**32:
                machine = 'x86_64'

        albo_inaczej machine w ('PowerPC', 'Power_Macintosh'):
            # Pick a sane name dla the PPC architecture.
            # See 'i386' case
            jeżeli sys.maxsize >= 2**32:
                machine = 'ppc64'
            inaczej:
                machine = 'ppc'

    zwróć (osname, release, machine)
