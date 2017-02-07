zaimportuj sys, os
zaimportuj contextlib
zaimportuj subprocess

# find_library(name) returns the pathname of a library, albo Nic.
jeżeli os.name == "nt":

    def _get_build_version():
        """Return the version of MSVC that was used to build Python.

        For Python 2.3 oraz up, the version number jest included w
        sys.version.  For earlier versions, assume the compiler jest MSVC 6.
        """
        # This function was copied z Lib/distutils/msvccompiler.py
        prefix = "MSC v."
        i = sys.version.find(prefix)
        jeżeli i == -1:
            zwróć 6
        i = i + len(prefix)
        s, rest = sys.version[i:].split(" ", 1)
        majorVersion = int(s[:-2]) - 6
        jeżeli majorVersion >= 13:
            majorVersion += 1
        minorVersion = int(s[2:3]) / 10.0
        # I don't think paths are affected by minor version w version 6
        jeżeli majorVersion == 6:
            minorVersion = 0
        jeżeli majorVersion >= 6:
            zwróć majorVersion + minorVersion
        # inaczej we don't know what version of the compiler this jest
        zwróć Nic

    def find_msvcrt():
        """Return the name of the VC runtime dll"""
        version = _get_build_version()
        jeżeli version jest Nic:
            # better be safe than sorry
            zwróć Nic
        jeżeli version <= 6:
            clibname = 'msvcrt'
        albo_inaczej version <= 13:
            clibname = 'msvcr%d' % (version * 10)
        inaczej:
            # CRT jest no longer directly loadable. See issue23606 dla the
            # discussion about alternative approaches.
            zwróć Nic

        # If python was built przy w debug mode
        zaimportuj importlib.machinery
        jeżeli '_d.pyd' w importlib.machinery.EXTENSION_SUFFIXES:
            clibname += 'd'
        zwróć clibname+'.dll'

    def find_library(name):
        jeżeli name w ('c', 'm'):
            zwróć find_msvcrt()
        # See MSDN dla the REAL search order.
        dla directory w os.environ['PATH'].split(os.pathsep):
            fname = os.path.join(directory, name)
            jeżeli os.path.isfile(fname):
                zwróć fname
            jeżeli fname.lower().endswith(".dll"):
                kontynuuj
            fname = fname + ".dll"
            jeżeli os.path.isfile(fname):
                zwróć fname
        zwróć Nic

jeżeli os.name == "ce":
    # search path according to MSDN:
    # - absolute path specified by filename
    # - The .exe launch directory
    # - the Windows directory
    # - ROM dll files (where are they?)
    # - OEM specified search path: HKLM\Loader\SystemPath
    def find_library(name):
        zwróć name

jeżeli os.name == "posix" oraz sys.platform == "darwin":
    z ctypes.macholib.dyld zaimportuj dyld_find jako _dyld_find
    def find_library(name):
        possible = ['lib%s.dylib' % name,
                    '%s.dylib' % name,
                    '%s.framework/%s' % (name, name)]
        dla name w possible:
            spróbuj:
                zwróć _dyld_find(name)
            wyjąwszy ValueError:
                kontynuuj
        zwróć Nic

albo_inaczej os.name == "posix":
    # Andreas Degert's find functions, using gcc, /sbin/ldconfig, objdump
    zaimportuj re, tempfile

    def _findLib_gcc(name):
        expr = r'[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name)
        fdout, ccout = tempfile.mkstemp()
        os.close(fdout)
        cmd = 'jeżeli type gcc >/dev/null 2>&1; then CC=gcc; albo_inaczej type cc >/dev/null 2>&1; then CC=cc;inaczej exit 10; fi;' \
              'LANG=C LC_ALL=C $CC -Wl,-t -o ' + ccout + ' 2>&1 -l' + name
        spróbuj:
            f = os.popen(cmd)
            spróbuj:
                trace = f.read()
            w_końcu:
                rv = f.close()
        w_końcu:
            spróbuj:
                os.unlink(ccout)
            wyjąwszy FileNotFoundError:
                dalej
        jeżeli rv == 10:
            podnieś OSError('gcc albo cc command nie found')
        res = re.search(expr, trace)
        jeżeli nie res:
            zwróć Nic
        zwróć res.group(0)


    jeżeli sys.platform == "sunos5":
        # use /usr/ccs/bin/dump on solaris
        def _get_soname(f):
            jeżeli nie f:
                zwróć Nic
            cmd = "/usr/ccs/bin/dump -Lpv 2>/dev/null " + f
            przy contextlib.closing(os.popen(cmd)) jako f:
                data = f.read()
            res = re.search(r'\[.*\]\sSONAME\s+([^\s]+)', data)
            jeżeli nie res:
                zwróć Nic
            zwróć res.group(1)
    inaczej:
        def _get_soname(f):
            # assuming GNU binutils / ELF
            jeżeli nie f:
                zwróć Nic
            cmd = 'jeżeli ! type objdump >/dev/null 2>&1; then exit 10; fi;' \
                  "objdump -p -j .dynamic 2>/dev/null " + f
            f = os.popen(cmd)
            spróbuj:
                dump = f.read()
            w_końcu:
                rv = f.close()
            jeżeli rv == 10:
                podnieś OSError('objdump command nie found')
            res = re.search(r'\sSONAME\s+([^\s]+)', dump)
            jeżeli nie res:
                zwróć Nic
            zwróć res.group(1)

    jeżeli sys.platform.startswith(("freebsd", "openbsd", "dragonfly")):

        def _num_version(libname):
            # "libxyz.so.MAJOR.MINOR" => [ MAJOR, MINOR ]
            parts = libname.split(".")
            nums = []
            spróbuj:
                dopóki parts:
                    nums.insert(0, int(parts.pop()))
            wyjąwszy ValueError:
                dalej
            zwróć nums albo [ sys.maxsize ]

        def find_library(name):
            ename = re.escape(name)
            expr = r':-l%s\.\S+ => \S*/(lib%s\.\S+)' % (ename, ename)
            przy contextlib.closing(os.popen('/sbin/ldconfig -r 2>/dev/null')) jako f:
                data = f.read()
            res = re.findall(expr, data)
            jeżeli nie res:
                zwróć _get_soname(_findLib_gcc(name))
            res.sort(key=_num_version)
            zwróć res[-1]

    albo_inaczej sys.platform == "sunos5":

        def _findLib_crle(name, is64):
            jeżeli nie os.path.exists('/usr/bin/crle'):
                zwróć Nic

            jeżeli is64:
                cmd = 'env LC_ALL=C /usr/bin/crle -64 2>/dev/null'
            inaczej:
                cmd = 'env LC_ALL=C /usr/bin/crle 2>/dev/null'

            przy contextlib.closing(os.popen(cmd)) jako f:
                dla line w f.readlines():
                    line = line.strip()
                    jeżeli line.startswith('Default Library Path (ELF):'):
                        paths = line.split()[4]

            jeżeli nie paths:
                zwróć Nic

            dla dir w paths.split(":"):
                libfile = os.path.join(dir, "lib%s.so" % name)
                jeżeli os.path.exists(libfile):
                    zwróć libfile

            zwróć Nic

        def find_library(name, is64 = Nieprawda):
            zwróć _get_soname(_findLib_crle(name, is64) albo _findLib_gcc(name))

    inaczej:

        def _findSoname_ldconfig(name):
            zaimportuj struct
            jeżeli struct.calcsize('l') == 4:
                machine = os.uname().machine + '-32'
            inaczej:
                machine = os.uname().machine + '-64'
            mach_map = {
                'x86_64-64': 'libc6,x86-64',
                'ppc64-64': 'libc6,64bit',
                'sparc64-64': 'libc6,64bit',
                's390x-64': 'libc6,64bit',
                'ia64-64': 'libc6,IA-64',
                }
            abi_type = mach_map.get(machine, 'libc6')

            # XXX assuming GLIBC's ldconfig (przy option -p)
            regex = os.fsencode(
                '\s+(lib%s\.[^\s]+)\s+\(%s' % (re.escape(name), abi_type))
            spróbuj:
                przy subprocess.Popen(['/sbin/ldconfig', '-p'],
                                      stdin=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL,
                                      stdout=subprocess.PIPE,
                                      env={'LC_ALL': 'C', 'LANG': 'C'}) jako p:
                    res = re.search(regex, p.stdout.read())
                    jeżeli res:
                        zwróć os.fsdecode(res.group(1))
            wyjąwszy OSError:
                dalej

        def find_library(name):
            zwróć _findSoname_ldconfig(name) albo _get_soname(_findLib_gcc(name))

################################################################
# test code

def test():
    z ctypes zaimportuj cdll
    jeżeli os.name == "nt":
        print(cdll.msvcrt)
        print(cdll.load("msvcrt"))
        print(find_library("msvcrt"))

    jeżeli os.name == "posix":
        # find oraz load_version
        print(find_library("m"))
        print(find_library("c"))
        print(find_library("bz2"))

        # getattr
##        print cdll.m
##        print cdll.bz2

        # load
        jeżeli sys.platform == "darwin":
            print(cdll.LoadLibrary("libm.dylib"))
            print(cdll.LoadLibrary("libcrypto.dylib"))
            print(cdll.LoadLibrary("libSystem.dylib"))
            print(cdll.LoadLibrary("System.framework/System"))
        inaczej:
            print(cdll.LoadLibrary("libm.so"))
            print(cdll.LoadLibrary("libcrypt.so"))
            print(find_library("crypt"))

jeżeli __name__ == "__main__":
    test()
