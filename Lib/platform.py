#!/usr/bin/env python3

""" This module tries to retrieve jako much platform-identifying data as
    possible. It makes this information available via function APIs.

    If called z the command line, it prints the platform
    information concatenated jako single string to stdout. The output
    format jest useable jako part of a filename.

"""
#    This module jest maintained by Marc-Andre Lemburg <mal@egenix.com>.
#    If you find problems, please submit bug reports/patches via the
#    Python bug tracker (http://bugs.python.org) oraz assign them to "lemburg".
#
#    Still needed:
#    * more support dla WinCE
#    * support dla MS-DOS (PythonDX ?)
#    * support dla Amiga oraz other still unsupported platforms running Python
#    * support dla additional Linux distributions
#
#    Many thanks to all those who helped adding platform-specific
#    checks (in no particular order):
#
#      Charles G Waldman, David Arnold, Gordon McMillan, Ben Darnell,
#      Jeff Bauer, Cliff Crawford, Ivan Van Laningham, Josef
#      Betancourt, Randall Hopper, Karl Putland, John Farrell, Greg
#      Andruk, Just van Rossum, Thomas Heller, Mark R. Levinson, Mark
#      Hammond, Bill Tutt, Hans Nowak, Uwe Zessin (OpenVMS support),
#      Colin Kong, Trent Mick, Guido van Rossum, Anthony Baxter
#
#    History:
#
#    <see CVS oraz SVN checkin messages dla history>
#
#    1.0.7 - added DEV_NULL
#    1.0.6 - added linux_distribution()
#    1.0.5 - fixed Java support to allow running the module on Jython
#    1.0.4 - added IronPython support
#    1.0.3 - added normalization of Windows system name
#    1.0.2 - added more Windows support
#    1.0.1 - reformatted to make doc.py happy
#    1.0.0 - reformatted a bit oraz checked into Python CVS
#    0.8.0 - added sys.version parser oraz various new access
#            APIs (python_version(), python_compiler(), etc.)
#    0.7.2 - fixed architecture() to use sizeof(pointer) where available
#    0.7.1 - added support dla Caldera OpenLinux
#    0.7.0 - some fixes dla WinCE; untabified the source file
#    0.6.2 - support dla OpenVMS - requires version 1.5.2-V006 albo higher oraz
#            vms_lib.getsyi() configured
#    0.6.1 - added code to prevent 'uname -p' on platforms which are
#            known nie to support it
#    0.6.0 - fixed win32_ver() to hopefully work on Win95,98,NT oraz Win2k;
#            did some cleanup of the interfaces - some APIs have changed
#    0.5.5 - fixed another type w the MacOS code... should have
#            used more coffee today ;-)
#    0.5.4 - fixed a few typos w the MacOS code
#    0.5.3 - added experimental MacOS support; added better popen()
#            workarounds w _syscmd_ver() -- still nie 100% elegant
#            though
#    0.5.2 - fixed uname() to zwróć '' instead of 'unknown' w all
#            zwróć values (the system uname command tends to zwróć
#            'unknown' instead of just leaving the field emtpy)
#    0.5.1 - included code dla slackware dist; added exception handlers
#            to cover up situations where platforms don't have os.popen
#            (e.g. Mac) albo fail on socket.gethostname(); fixed libc
#            detection RE
#    0.5.0 - changed the API names referring to system commands to *syscmd*;
#            added java_ver(); made syscmd_ver() a private
#            API (was system_ver() w previous versions) -- use uname()
#            instead; extended the win32_ver() to also zwróć processor
#            type information
#    0.4.0 - added win32_ver() oraz modified the platform() output dla WinXX
#    0.3.4 - fixed a bug w _follow_symlinks()
#    0.3.3 - fixed popen() oraz "file" command invokation bugs
#    0.3.2 - added architecture() API oraz support dla it w platform()
#    0.3.1 - fixed syscmd_ver() RE to support Windows NT
#    0.3.0 - added system alias support
#    0.2.3 - removed 'wince' again... oh well.
#    0.2.2 - added 'wince' to syscmd_ver() supported platforms
#    0.2.1 - added cache logic oraz changed the platform string format
#    0.2.0 - changed the API to use functions instead of module globals
#            since some action take too long to be run on module import
#    0.1.0 - first release
#
#    You can always get the latest version of this module at:
#
#             http://www.egenix.com/files/python/platform.py
#
#    If that URL should fail, try contacting the author.

__copyright__ = """
    Copyright (c) 1999-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2010, eGenix.com Software GmbH; mailto:info@egenix.com

    Permission to use, copy, modify, oraz distribute this software oraz its
    documentation dla any purpose oraz without fee albo royalty jest hereby granted,
    provided that the above copyright notice appear w all copies oraz that
    both that copyright notice oraz this permission notice appear w
    supporting documentation albo portions thereof, including modifications,
    that you make.

    EGENIX.COM SOFTWARE GMBH DISCLAIMS ALL WARRANTIES WITH REGARD TO
    THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
    INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
    FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
    NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
    WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !

"""

__version__ = '1.0.7'

zaimportuj collections
zaimportuj sys, os, re, subprocess

zaimportuj warnings

### Globals & Constants

# Determine the platform's /dev/null device
spróbuj:
    DEV_NULL = os.devnull
wyjąwszy AttributeError:
    # os.devnull was added w Python 2.4, so emulate it dla earlier
    # Python versions
    jeżeli sys.platform w ('dos', 'win32', 'win16'):
        # Use the old CP/M NUL jako device name
        DEV_NULL = 'NUL'
    inaczej:
        # Standard Unix uses /dev/null
        DEV_NULL = '/dev/null'

# Directory to search dla configuration information on Unix.
# Constant used by test_platform to test linux_distribution().
_UNIXCONFDIR = '/etc'

### Platform specific APIs

_libc_search = re.compile(b'(__libc_init)'
                          b'|'
                          b'(GLIBC_([0-9.]+))'
                          b'|'
                          br'(libc(_\w+)?\.so(?:\.(\d[0-9.]*))?)', re.ASCII)

def libc_ver(executable=sys.executable, lib='', version='',

             chunksize=16384):

    """ Tries to determine the libc version that the file executable
        (which defaults to the Python interpreter) jest linked against.

        Returns a tuple of strings (lib,version) which default to the
        given parameters w case the lookup fails.

        Note that the function has intimate knowledge of how different
        libc versions add symbols to the executable oraz thus jest probably
        only useable dla executables compiled using gcc.

        The file jest read oraz scanned w chunks of chunksize bytes.

    """
    jeżeli hasattr(os.path, 'realpath'):
        # Python 2.2 introduced os.path.realpath(); it jest used
        # here to work around problems przy Cygwin nie being
        # able to open symlinks dla reading
        executable = os.path.realpath(executable)
    przy open(executable, 'rb') jako f:
        binary = f.read(chunksize)
        pos = 0
        dopóki 1:
            jeżeli b'libc' w binary albo b'GLIBC' w binary:
                m = _libc_search.search(binary, pos)
            inaczej:
                m = Nic
            jeżeli nie m:
                binary = f.read(chunksize)
                jeżeli nie binary:
                    przerwij
                pos = 0
                kontynuuj
            libcinit, glibc, glibcversion, so, threads, soversion = [
                s.decode('latin1') jeżeli s jest nie Nic inaczej s
                dla s w m.groups()]
            jeżeli libcinit oraz nie lib:
                lib = 'libc'
            albo_inaczej glibc:
                jeżeli lib != 'glibc':
                    lib = 'glibc'
                    version = glibcversion
                albo_inaczej glibcversion > version:
                    version = glibcversion
            albo_inaczej so:
                jeżeli lib != 'glibc':
                    lib = 'libc'
                    jeżeli soversion oraz soversion > version:
                        version = soversion
                    jeżeli threads oraz version[-len(threads):] != threads:
                        version = version + threads
            pos = m.end()
    zwróć lib, version

def _dist_try_harder(distname, version, id):

    """ Tries some special tricks to get the distribution
        information w case the default method fails.

        Currently supports older SuSE Linux, Caldera OpenLinux oraz
        Slackware Linux distributions.

    """
    jeżeli os.path.exists('/var/adm/inst-log/info'):
        # SuSE Linux stores distribution information w that file
        distname = 'SuSE'
        dla line w open('/var/adm/inst-log/info'):
            tv = line.split()
            jeżeli len(tv) == 2:
                tag, value = tv
            inaczej:
                kontynuuj
            jeżeli tag == 'MIN_DIST_VERSION':
                version = value.strip()
            albo_inaczej tag == 'DIST_IDENT':
                values = value.split('-')
                id = values[2]
        zwróć distname, version, id

    jeżeli os.path.exists('/etc/.installed'):
        # Caldera OpenLinux has some infos w that file (thanks to Colin Kong)
        dla line w open('/etc/.installed'):
            pkg = line.split('-')
            jeżeli len(pkg) >= 2 oraz pkg[0] == 'OpenLinux':
                # XXX does Caldera support non Intel platforms ? If yes,
                #     where can we find the needed id ?
                zwróć 'OpenLinux', pkg[1], id

    jeżeli os.path.isdir('/usr/lib/setup'):
        # Check dla slackware version tag file (thanks to Greg Andruk)
        verfiles = os.listdir('/usr/lib/setup')
        dla n w range(len(verfiles)-1, -1, -1):
            jeżeli verfiles[n][:14] != 'slack-version-':
                usuń verfiles[n]
        jeżeli verfiles:
            verfiles.sort()
            distname = 'slackware'
            version = verfiles[-1][14:]
            zwróć distname, version, id

    zwróć distname, version, id

_release_filename = re.compile(r'(\w+)[-_](release|version)', re.ASCII)
_lsb_release_version = re.compile(r'(.+)'
                                   ' release '
                                   '([\d.]+)'
                                   '[^(]*(?:\((.+)\))?', re.ASCII)
_release_version = re.compile(r'([^0-9]+)'
                               '(?: release )?'
                               '([\d.]+)'
                               '[^(]*(?:\((.+)\))?', re.ASCII)

# See also http://www.novell.com/coolsolutions/feature/11251.html
# oraz http://linuxmafia.com/faq/Admin/release-files.html
# oraz http://data.linux-ntfs.org/rpm/whichrpm
# oraz http://www.die.net/doc/linux/man/man1/lsb_release.1.html

_supported_dists = (
    'SuSE', 'debian', 'fedora', 'redhat', 'centos',
    'mandrake', 'mandriva', 'rocks', 'slackware', 'yellowdog', 'gentoo',
    'UnitedLinux', 'turbolinux', 'arch', 'mageia')

def _parse_release_file(firstline):

    # Default to empty 'version' oraz 'id' strings.  Both defaults are used
    # when 'firstline' jest empty.  'id' defaults to empty when an id can nie
    # be deduced.
    version = ''
    id = ''

    # Parse the first line
    m = _lsb_release_version.match(firstline)
    jeżeli m jest nie Nic:
        # LSB format: "distro release x.x (codename)"
        zwróć tuple(m.groups())

    # Pre-LSB format: "distro x.x (codename)"
    m = _release_version.match(firstline)
    jeżeli m jest nie Nic:
        zwróć tuple(m.groups())

    # Unknown format... take the first two words
    l = firstline.strip().split()
    jeżeli l:
        version = l[0]
        jeżeli len(l) > 1:
            id = l[1]
    zwróć '', version, id

def linux_distribution(distname='', version='', id='',

                       supported_dists=_supported_dists,
                       full_distribution_name=1):
    zaimportuj warnings
    warnings.warn("dist() oraz linux_distribution() functions are deprecated "
                  "in Python 3.5 oraz will be removed w Python 3.7",
                  PendingDeprecationWarning, stacklevel=2)
    zwróć _linux_distribution(distname, version, id, supported_dists,
                               full_distribution_name)

def _linux_distribution(distname, version, id, supported_dists,
                        full_distribution_name):

    """ Tries to determine the name of the Linux OS distribution name.

        The function first looks dla a distribution release file w
        /etc oraz then reverts to _dist_try_harder() w case no
        suitable files are found.

        supported_dists may be given to define the set of Linux
        distributions to look for. It defaults to a list of currently
        supported Linux distributions identified by their release file
        name.

        If full_distribution_name jest true (default), the full
        distribution read z the OS jest returned. Otherwise the short
        name taken z supported_dists jest used.

        Returns a tuple (distname, version, id) which default to the
        args given jako parameters.

    """
    spróbuj:
        etc = os.listdir(_UNIXCONFDIR)
    wyjąwszy OSError:
        # Probably nie a Unix system
        zwróć distname, version, id
    etc.sort()
    dla file w etc:
        m = _release_filename.match(file)
        jeżeli m jest nie Nic:
            _distname, dummy = m.groups()
            jeżeli _distname w supported_dists:
                distname = _distname
                przerwij
    inaczej:
        zwróć _dist_try_harder(distname, version, id)

    # Read the first line
    przy open(os.path.join(_UNIXCONFDIR, file), 'r',
              encoding='utf-8', errors='surrogateescape') jako f:
        firstline = f.readline()
    _distname, _version, _id = _parse_release_file(firstline)

    jeżeli _distname oraz full_distribution_name:
        distname = _distname
    jeżeli _version:
        version = _version
    jeżeli _id:
        id = _id
    zwróć distname, version, id

# To maintain backwards compatibility:

def dist(distname='', version='', id='',

         supported_dists=_supported_dists):

    """ Tries to determine the name of the Linux OS distribution name.

        The function first looks dla a distribution release file w
        /etc oraz then reverts to _dist_try_harder() w case no
        suitable files are found.

        Returns a tuple (distname, version, id) which default to the
        args given jako parameters.

    """
    zaimportuj warnings
    warnings.warn("dist() oraz linux_distribution() functions are deprecated "
                  "in Python 3.5 oraz will be removed w Python 3.7",
                  PendingDeprecationWarning, stacklevel=2)
    zwróć _linux_distribution(distname, version, id,
                               supported_dists=supported_dists,
                               full_distribution_name=0)

def popen(cmd, mode='r', bufsize=-1):

    """ Portable popen() interface.
    """
    zaimportuj warnings
    warnings.warn('use os.popen instead', DeprecationWarning, stacklevel=2)
    zwróć os.popen(cmd, mode, bufsize)

def _norm_version(version, build=''):

    """ Normalize the version oraz build strings oraz zwróć a single
        version string using the format major.minor.build (or patchlevel).
    """
    l = version.split('.')
    jeżeli build:
        l.append(build)
    spróbuj:
        ints = map(int, l)
    wyjąwszy ValueError:
        strings = l
    inaczej:
        strings = list(map(str, ints))
    version = '.'.join(strings[:3])
    zwróć version

_ver_output = re.compile(r'(?:([\w ]+) ([\w.]+) '
                         '.*'
                         '\[.* ([\d.]+)\])')

# Examples of VER command output:
#
#   Windows 2000:  Microsoft Windows 2000 [Version 5.00.2195]
#   Windows XP:    Microsoft Windows XP [Version 5.1.2600]
#   Windows Vista: Microsoft Windows [Version 6.0.6002]
#
# Note that the "Version" string gets localized on different
# Windows versions.

def _syscmd_ver(system='', release='', version='',

               supported_platforms=('win32', 'win16', 'dos')):

    """ Tries to figure out the OS version used oraz returns
        a tuple (system, release, version).

        It uses the "ver" shell command dla this which jest known
        to exists on Windows, DOS. XXX Others too ?

        In case this fails, the given parameters are used as
        defaults.

    """
    jeżeli sys.platform nie w supported_platforms:
        zwróć system, release, version

    # Try some common cmd strings
    dla cmd w ('ver', 'command /c ver', 'cmd /c ver'):
        spróbuj:
            pipe = os.popen(cmd)
            info = pipe.read()
            jeżeli pipe.close():
                podnieś OSError('command failed')
            # XXX How can I suppress shell errors z being written
            #     to stderr ?
        wyjąwszy OSError jako why:
            #print 'Command %s failed: %s' % (cmd, why)
            kontynuuj
        inaczej:
            przerwij
    inaczej:
        zwróć system, release, version

    # Parse the output
    info = info.strip()
    m = _ver_output.match(info)
    jeżeli m jest nie Nic:
        system, release, version = m.groups()
        # Strip trailing dots z version oraz release
        jeżeli release[-1] == '.':
            release = release[:-1]
        jeżeli version[-1] == '.':
            version = version[:-1]
        # Normalize the version oraz build strings (eliminating additional
        # zeros)
        version = _norm_version(version)
    zwróć system, release, version

def _win32_getvalue(key, name, default=''):

    """ Read a value dla name z the registry key.

        In case this fails, default jest returned.

    """
    spróbuj:
        # Use win32api jeżeli available
        z win32api zaimportuj RegQueryValueEx
    wyjąwszy ImportError:
        # On Python 2.0 oraz later, emulate using winreg
        zaimportuj winreg
        RegQueryValueEx = winreg.QueryValueEx
    spróbuj:
        zwróć RegQueryValueEx(key, name)
    wyjąwszy:
        zwróć default

def win32_ver(release='', version='', csd='', ptype=''):

    """ Get additional version information z the Windows Registry
        oraz zwróć a tuple (version, csd, ptype) referring to version
        number, CSD level (service pack), oraz OS type (multi/single
        processor).

        As a hint: ptype returns 'Uniprocessor Free' on single
        processor NT machines oraz 'Multiprocessor Free' on multi
        processor machines. The 'Free' refers to the OS version being
        free of debugging code. It could also state 'Checked' which
        means the OS version uses debugging code, i.e. code that
        checks arguments, ranges, etc. (Thomas Heller).

        Note: this function works best przy Mark Hammond's win32
        package installed, but also on Python 2.3 oraz later. It
        obviously only runs on Win32 compatible platforms.

    """
    # XXX Is there any way to find out the processor type on WinXX ?
    # XXX Is win32 available on Windows CE ?
    #
    # Adapted z code posted by Karl Putland to comp.lang.python.
    #
    # The mappings between reg. values oraz release names can be found
    # here: http://msdn.microsoft.com/library/en-us/sysinfo/base/osversioninfo_str.asp

    # Import the needed APIs
    spróbuj:
        z win32api zaimportuj RegQueryValueEx, RegOpenKeyEx, \
             RegCloseKey, GetVersionEx
        z win32con zaimportuj HKEY_LOCAL_MACHINE, VER_PLATFORM_WIN32_NT, \
             VER_PLATFORM_WIN32_WINDOWS, VER_NT_WORKSTATION
    wyjąwszy ImportError:
        # Emulate the win32api module using Python APIs
        spróbuj:
            sys.getwindowsversion
        wyjąwszy AttributeError:
            # No emulation possible, so zwróć the defaults...
            zwróć release, version, csd, ptype
        inaczej:
            # Emulation using winreg (added w Python 2.0) oraz
            # sys.getwindowsversion() (added w Python 2.3)
            zaimportuj winreg
            GetVersionEx = sys.getwindowsversion
            RegQueryValueEx = winreg.QueryValueEx
            RegOpenKeyEx = winreg.OpenKeyEx
            RegCloseKey = winreg.CloseKey
            HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
            VER_PLATFORM_WIN32_WINDOWS = 1
            VER_PLATFORM_WIN32_NT = 2
            VER_NT_WORKSTATION = 1
            VER_NT_SERVER = 3
            REG_SZ = 1

    # Find out the registry key oraz some general version infos
    winver = GetVersionEx()
    maj, min, buildno, plat, csd = winver
    version = '%i.%i.%i' % (maj, min, buildno & 0xFFFF)
    jeżeli hasattr(winver, "service_pack"):
        jeżeli winver.service_pack != "":
            csd = 'SP%s' % winver.service_pack_major
    inaczej:
        jeżeli csd[:13] == 'Service Pack ':
            csd = 'SP' + csd[13:]

    jeżeli plat == VER_PLATFORM_WIN32_WINDOWS:
        regkey = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion'
        # Try to guess the release name
        jeżeli maj == 4:
            jeżeli min == 0:
                release = '95'
            albo_inaczej min == 10:
                release = '98'
            albo_inaczej min == 90:
                release = 'Me'
            inaczej:
                release = 'postMe'
        albo_inaczej maj == 5:
            release = '2000'

    albo_inaczej plat == VER_PLATFORM_WIN32_NT:
        regkey = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
        jeżeli maj <= 4:
            release = 'NT'
        albo_inaczej maj == 5:
            jeżeli min == 0:
                release = '2000'
            albo_inaczej min == 1:
                release = 'XP'
            albo_inaczej min == 2:
                release = '2003Server'
            inaczej:
                release = 'post2003'
        albo_inaczej maj == 6:
            jeżeli hasattr(winver, "product_type"):
                product_type = winver.product_type
            inaczej:
                product_type = VER_NT_WORKSTATION
                # Without an OSVERSIONINFOEX capable sys.getwindowsversion(),
                # albo help z the registry, we cannot properly identify
                # non-workstation versions.
                spróbuj:
                    key = RegOpenKeyEx(HKEY_LOCAL_MACHINE, regkey)
                    name, type = RegQueryValueEx(key, "ProductName")
                    # Discard any type that isn't REG_SZ
                    jeżeli type == REG_SZ oraz name.find("Server") != -1:
                        product_type = VER_NT_SERVER
                wyjąwszy OSError:
                    # Use default of VER_NT_WORKSTATION
                    dalej

            jeżeli min == 0:
                jeżeli product_type == VER_NT_WORKSTATION:
                    release = 'Vista'
                inaczej:
                    release = '2008Server'
            albo_inaczej min == 1:
                jeżeli product_type == VER_NT_WORKSTATION:
                    release = '7'
                inaczej:
                    release = '2008ServerR2'
            albo_inaczej min == 2:
                jeżeli product_type == VER_NT_WORKSTATION:
                    release = '8'
                inaczej:
                    release = '2012Server'
            inaczej:
                release = 'post2012Server'

    inaczej:
        jeżeli nie release:
            # E.g. Win3.1 przy win32s
            release = '%i.%i' % (maj, min)
        zwróć release, version, csd, ptype

    # Open the registry key
    spróbuj:
        keyCurVer = RegOpenKeyEx(HKEY_LOCAL_MACHINE, regkey)
        # Get a value to make sure the key exists...
        RegQueryValueEx(keyCurVer, 'SystemRoot')
    wyjąwszy:
        zwróć release, version, csd, ptype

    # Parse values
    #subversion = _win32_getvalue(keyCurVer,
    #                            'SubVersionNumber',
    #                            ('',1))[0]
    #jeżeli subversion:
    #   release = release + subversion # 95a, 95b, etc.
    build = _win32_getvalue(keyCurVer,
                            'CurrentBuildNumber',
                            ('', 1))[0]
    ptype = _win32_getvalue(keyCurVer,
                           'CurrentType',
                           (ptype, 1))[0]

    # Normalize version
    version = _norm_version(version, build)

    # Close key
    RegCloseKey(keyCurVer)
    zwróć release, version, csd, ptype

def _mac_ver_xml():
    fn = '/System/Library/CoreServices/SystemVersion.plist'
    jeżeli nie os.path.exists(fn):
        zwróć Nic

    spróbuj:
        zaimportuj plistlib
    wyjąwszy ImportError:
        zwróć Nic

    przy open(fn, 'rb') jako f:
        pl = plistlib.load(f)
    release = pl['ProductVersion']
    versioninfo = ('', '', '')
    machine = os.uname().machine
    jeżeli machine w ('ppc', 'Power Macintosh'):
        # Canonical name
        machine = 'PowerPC'

    zwróć release, versioninfo, machine


def mac_ver(release='', versioninfo=('', '', ''), machine=''):

    """ Get MacOS version information oraz zwróć it jako tuple (release,
        versioninfo, machine) przy versioninfo being a tuple (version,
        dev_stage, non_release_version).

        Entries which cannot be determined are set to the parameter values
        which default to ''. All tuple entries are strings.
    """

    # First try reading the information z an XML file which should
    # always be present
    info = _mac_ver_xml()
    jeżeli info jest nie Nic:
        zwróć info

    # If that also doesn't work zwróć the default values
    zwróć release, versioninfo, machine

def _java_getprop(name, default):

    z java.lang zaimportuj System
    spróbuj:
        value = System.getProperty(name)
        jeżeli value jest Nic:
            zwróć default
        zwróć value
    wyjąwszy AttributeError:
        zwróć default

def java_ver(release='', vendor='', vminfo=('', '', ''), osinfo=('', '', '')):

    """ Version interface dla Jython.

        Returns a tuple (release, vendor, vminfo, osinfo) przy vminfo being
        a tuple (vm_name, vm_release, vm_vendor) oraz osinfo being a
        tuple (os_name, os_version, os_arch).

        Values which cannot be determined are set to the defaults
        given jako parameters (which all default to '').

    """
    # Import the needed APIs
    spróbuj:
        zaimportuj java.lang
    wyjąwszy ImportError:
        zwróć release, vendor, vminfo, osinfo

    vendor = _java_getprop('java.vendor', vendor)
    release = _java_getprop('java.version', release)
    vm_name, vm_release, vm_vendor = vminfo
    vm_name = _java_getprop('java.vm.name', vm_name)
    vm_vendor = _java_getprop('java.vm.vendor', vm_vendor)
    vm_release = _java_getprop('java.vm.version', vm_release)
    vminfo = vm_name, vm_release, vm_vendor
    os_name, os_version, os_arch = osinfo
    os_arch = _java_getprop('java.os.arch', os_arch)
    os_name = _java_getprop('java.os.name', os_name)
    os_version = _java_getprop('java.os.version', os_version)
    osinfo = os_name, os_version, os_arch

    zwróć release, vendor, vminfo, osinfo

### System name aliasing

def system_alias(system, release, version):

    """ Returns (system, release, version) aliased to common
        marketing names used dla some systems.

        It also does some reordering of the information w some cases
        where it would otherwise cause confusion.

    """
    jeżeli system == 'Rhapsody':
        # Apple's BSD derivative
        # XXX How can we determine the marketing release number ?
        zwróć 'MacOS X Server', system+release, version

    albo_inaczej system == 'SunOS':
        # Sun's OS
        jeżeli release < '5':
            # These releases use the old name SunOS
            zwróć system, release, version
        # Modify release (marketing release = SunOS release - 3)
        l = release.split('.')
        jeżeli l:
            spróbuj:
                major = int(l[0])
            wyjąwszy ValueError:
                dalej
            inaczej:
                major = major - 3
                l[0] = str(major)
                release = '.'.join(l)
        jeżeli release < '6':
            system = 'Solaris'
        inaczej:
            # XXX Whatever the new SunOS marketing name is...
            system = 'Solaris'

    albo_inaczej system == 'IRIX64':
        # IRIX reports IRIX64 on platforms przy 64-bit support; yet it
        # jest really a version oraz nie a different platform, since 32-bit
        # apps are also supported..
        system = 'IRIX'
        jeżeli version:
            version = version + ' (64bit)'
        inaczej:
            version = '64bit'

    albo_inaczej system w ('win32', 'win16'):
        # In case one of the other tricks
        system = 'Windows'

    zwróć system, release, version

### Various internal helpers

def _platform(*args):

    """ Helper to format the platform string w a filename
        compatible format e.g. "system-version-machine".
    """
    # Format the platform string
    platform = '-'.join(x.strip() dla x w filter(len, args))

    # Cleanup some possible filename obstacles...
    platform = platform.replace(' ', '_')
    platform = platform.replace('/', '-')
    platform = platform.replace('\\', '-')
    platform = platform.replace(':', '-')
    platform = platform.replace(';', '-')
    platform = platform.replace('"', '-')
    platform = platform.replace('(', '-')
    platform = platform.replace(')', '-')

    # No need to report 'unknown' information...
    platform = platform.replace('unknown', '')

    # Fold '--'s oraz remove trailing '-'
    dopóki 1:
        cleaned = platform.replace('--', '-')
        jeżeli cleaned == platform:
            przerwij
        platform = cleaned
    dopóki platform[-1] == '-':
        platform = platform[:-1]

    zwróć platform

def _node(default=''):

    """ Helper to determine the node name of this machine.
    """
    spróbuj:
        zaimportuj socket
    wyjąwszy ImportError:
        # No sockets...
        zwróć default
    spróbuj:
        zwróć socket.gethostname()
    wyjąwszy OSError:
        # Still nie working...
        zwróć default

def _follow_symlinks(filepath):

    """ In case filepath jest a symlink, follow it until a
        real file jest reached.
    """
    filepath = os.path.abspath(filepath)
    dopóki os.path.islink(filepath):
        filepath = os.path.normpath(
            os.path.join(os.path.dirname(filepath), os.readlink(filepath)))
    zwróć filepath

def _syscmd_uname(option, default=''):

    """ Interface to the system's uname command.
    """
    jeżeli sys.platform w ('dos', 'win32', 'win16'):
        # XXX Others too ?
        zwróć default
    spróbuj:
        f = os.popen('uname %s 2> %s' % (option, DEV_NULL))
    wyjąwszy (AttributeError, OSError):
        zwróć default
    output = f.read().strip()
    rc = f.close()
    jeżeli nie output albo rc:
        zwróć default
    inaczej:
        zwróć output

def _syscmd_file(target, default=''):

    """ Interface to the system's file command.

        The function uses the -b option of the file command to have it
        omit the filename w its output. Follow the symlinks. It returns
        default w case the command should fail.

    """
    jeżeli sys.platform w ('dos', 'win32', 'win16'):
        # XXX Others too ?
        zwróć default
    target = _follow_symlinks(target)
    spróbuj:
        proc = subprocess.Popen(['file', target],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    wyjąwszy (AttributeError, OSError):
        zwróć default
    output = proc.communicate()[0].decode('latin-1')
    rc = proc.wait()
    jeżeli nie output albo rc:
        zwróć default
    inaczej:
        zwróć output

### Information about the used architecture

# Default values dla architecture; non-empty strings override the
# defaults given jako parameters
_default_architecture = {
    'win32': ('', 'WindowsPE'),
    'win16': ('', 'Windows'),
    'dos': ('', 'MSDOS'),
}

def architecture(executable=sys.executable, bits='', linkage=''):

    """ Queries the given executable (defaults to the Python interpreter
        binary) dla various architecture information.

        Returns a tuple (bits, linkage) which contains information about
        the bit architecture oraz the linkage format used dla the
        executable. Both values are returned jako strings.

        Values that cannot be determined are returned jako given by the
        parameter presets. If bits jest given jako '', the sizeof(pointer)
        (or sizeof(long) on Python version < 1.5.2) jest used as
        indicator dla the supported pointer size.

        The function relies on the system's "file" command to do the
        actual work. This jest available on most jeżeli nie all Unix
        platforms. On some non-Unix platforms where the "file" command
        does nie exist oraz the executable jest set to the Python interpreter
        binary defaults z _default_architecture are used.

    """
    # Use the sizeof(pointer) jako default number of bits jeżeli nothing
    # inaczej jest given jako default.
    jeżeli nie bits:
        zaimportuj struct
        spróbuj:
            size = struct.calcsize('P')
        wyjąwszy struct.error:
            # Older installations can only query longs
            size = struct.calcsize('l')
        bits = str(size*8) + 'bit'

    # Get data z the 'file' system command
    jeżeli executable:
        fileout = _syscmd_file(executable, '')
    inaczej:
        fileout = ''

    jeżeli nie fileout oraz \
       executable == sys.executable:
        # "file" command did nie zwróć anything; we'll try to provide
        # some sensible defaults then...
        jeżeli sys.platform w _default_architecture:
            b, l = _default_architecture[sys.platform]
            jeżeli b:
                bits = b
            jeżeli l:
                linkage = l
        zwróć bits, linkage

    jeżeli 'executable' nie w fileout:
        # Format nie supported
        zwróć bits, linkage

    # Bits
    jeżeli '32-bit' w fileout:
        bits = '32bit'
    albo_inaczej 'N32' w fileout:
        # On Irix only
        bits = 'n32bit'
    albo_inaczej '64-bit' w fileout:
        bits = '64bit'

    # Linkage
    jeżeli 'ELF' w fileout:
        linkage = 'ELF'
    albo_inaczej 'PE' w fileout:
        # E.g. Windows uses this format
        jeżeli 'Windows' w fileout:
            linkage = 'WindowsPE'
        inaczej:
            linkage = 'PE'
    albo_inaczej 'COFF' w fileout:
        linkage = 'COFF'
    albo_inaczej 'MS-DOS' w fileout:
        linkage = 'MSDOS'
    inaczej:
        # XXX the A.OUT format also falls under this class...
        dalej

    zwróć bits, linkage

### Portable uname() interface

uname_result = collections.namedtuple("uname_result",
                    "system node release version machine processor")

_uname_cache = Nic

def uname():

    """ Fairly portable uname interface. Returns a tuple
        of strings (system, node, release, version, machine, processor)
        identifying the underlying platform.

        Note that unlike the os.uname function this also returns
        possible processor information jako an additional tuple entry.

        Entries which cannot be determined are set to ''.

    """
    global _uname_cache
    no_os_uname = 0

    jeżeli _uname_cache jest nie Nic:
        zwróć _uname_cache

    processor = ''

    # Get some infos z the builtin os.uname API...
    spróbuj:
        system, node, release, version, machine = os.uname()
    wyjąwszy AttributeError:
        no_os_uname = 1

    jeżeli no_os_uname albo nie list(filter(Nic, (system, node, release, version, machine))):
        # Hmm, no there jest either no uname albo uname has returned
        #'unknowns'... we'll have to poke around the system then.
        jeżeli no_os_uname:
            system = sys.platform
            release = ''
            version = ''
            node = _node()
            machine = ''

        use_syscmd_ver = 1

        # Try win32_ver() on win32 platforms
        jeżeli system == 'win32':
            release, version, csd, ptype = win32_ver()
            jeżeli release oraz version:
                use_syscmd_ver = 0
            # Try to use the PROCESSOR_* environment variables
            # available on Win XP oraz later; see
            # http://support.microsoft.com/kb/888731 oraz
            # http://www.geocities.com/rick_lively/MANUALS/ENV/MSWIN/PROCESSI.HTM
            jeżeli nie machine:
                # WOW64 processes mask the native architecture
                jeżeli "PROCESSOR_ARCHITEW6432" w os.environ:
                    machine = os.environ.get("PROCESSOR_ARCHITEW6432", '')
                inaczej:
                    machine = os.environ.get('PROCESSOR_ARCHITECTURE', '')
            jeżeli nie processor:
                processor = os.environ.get('PROCESSOR_IDENTIFIER', machine)

        # Try the 'ver' system command available on some
        # platforms
        jeżeli use_syscmd_ver:
            system, release, version = _syscmd_ver(system)
            # Normalize system to what win32_ver() normally returns
            # (_syscmd_ver() tends to zwróć the vendor name jako well)
            jeżeli system == 'Microsoft Windows':
                system = 'Windows'
            albo_inaczej system == 'Microsoft' oraz release == 'Windows':
                # Under Windows Vista oraz Windows Server 2008,
                # Microsoft changed the output of the ver command. The
                # release jest no longer printed.  This causes the
                # system oraz release to be misidentified.
                system = 'Windows'
                jeżeli '6.0' == version[:3]:
                    release = 'Vista'
                inaczej:
                    release = ''

        # In case we still don't know anything useful, we'll try to
        # help ourselves
        jeżeli system w ('win32', 'win16'):
            jeżeli nie version:
                jeżeli system == 'win32':
                    version = '32bit'
                inaczej:
                    version = '16bit'
            system = 'Windows'

        albo_inaczej system[:4] == 'java':
            release, vendor, vminfo, osinfo = java_ver()
            system = 'Java'
            version = ', '.join(vminfo)
            jeżeli nie version:
                version = vendor

    # System specific extensions
    jeżeli system == 'OpenVMS':
        # OpenVMS seems to have release oraz version mixed up
        jeżeli nie release albo release == '0':
            release = version
            version = ''
        # Get processor information
        spróbuj:
            zaimportuj vms_lib
        wyjąwszy ImportError:
            dalej
        inaczej:
            csid, cpu_number = vms_lib.getsyi('SYI$_CPU', 0)
            jeżeli (cpu_number >= 128):
                processor = 'Alpha'
            inaczej:
                processor = 'VAX'
    jeżeli nie processor:
        # Get processor information z the uname system command
        processor = _syscmd_uname('-p', '')

    #If any unknowns still exist, replace them przy ''s, which are more portable
    jeżeli system == 'unknown':
        system = ''
    jeżeli node == 'unknown':
        node = ''
    jeżeli release == 'unknown':
        release = ''
    jeżeli version == 'unknown':
        version = ''
    jeżeli machine == 'unknown':
        machine = ''
    jeżeli processor == 'unknown':
        processor = ''

    #  normalize name
    jeżeli system == 'Microsoft' oraz release == 'Windows':
        system = 'Windows'
        release = 'Vista'

    _uname_cache = uname_result(system, node, release, version,
                                machine, processor)
    zwróć _uname_cache

### Direct interfaces to some of the uname() zwróć values

def system():

    """ Returns the system/OS name, e.g. 'Linux', 'Windows' albo 'Java'.

        An empty string jest returned jeżeli the value cannot be determined.

    """
    zwróć uname().system

def node():

    """ Returns the computer's network name (which may nie be fully
        qualified)

        An empty string jest returned jeżeli the value cannot be determined.

    """
    zwróć uname().node

def release():

    """ Returns the system's release, e.g. '2.2.0' albo 'NT'

        An empty string jest returned jeżeli the value cannot be determined.

    """
    zwróć uname().release

def version():

    """ Returns the system's release version, e.g. '#3 on degas'

        An empty string jest returned jeżeli the value cannot be determined.

    """
    zwróć uname().version

def machine():

    """ Returns the machine type, e.g. 'i386'

        An empty string jest returned jeżeli the value cannot be determined.

    """
    zwróć uname().machine

def processor():

    """ Returns the (true) processor name, e.g. 'amdk6'

        An empty string jest returned jeżeli the value cannot be
        determined. Note that many platforms do nie provide this
        information albo simply zwróć the same value jako dla machine(),
        e.g.  NetBSD does this.

    """
    zwróć uname().processor

### Various APIs dla extracting information z sys.version

_sys_version_parser = re.compile(
    r'([\w.+]+)\s*'
    '\(#?([^,]+),\s*([\w ]+),\s*([\w :]+)\)\s*'
    '\[([^\]]+)\]?', re.ASCII)

_ironpython_sys_version_parser = re.compile(
    r'IronPython\s*'
    '([\d\.]+)'
    '(?: \(([\d\.]+)\))?'
    ' on (.NET [\d\.]+)', re.ASCII)

# IronPython covering 2.6 oraz 2.7
_ironpython26_sys_version_parser = re.compile(
    r'([\d.]+)\s*'
    '\(IronPython\s*'
    '[\d.]+\s*'
    '\(([\d.]+)\) on ([\w.]+ [\d.]+(?: \(\d+-bit\))?)\)'
)

_pypy_sys_version_parser = re.compile(
    r'([\w.+]+)\s*'
    '\(#?([^,]+),\s*([\w ]+),\s*([\w :]+)\)\s*'
    '\[PyPy [^\]]+\]?')

_sys_version_cache = {}

def _sys_version(sys_version=Nic):

    """ Returns a parsed version of Python's sys.version jako tuple
        (name, version, branch, revision, buildno, builddate, compiler)
        referring to the Python implementation name, version, branch,
        revision, build number, build date/time jako string oraz the compiler
        identification string.

        Note that unlike the Python sys.version, the returned value
        dla the Python version will always include the patchlevel (it
        defaults to '.0').

        The function returns empty strings dla tuple entries that
        cannot be determined.

        sys_version may be given to parse an alternative version
        string, e.g. jeżeli the version was read z a different Python
        interpreter.

    """
    # Get the Python version
    jeżeli sys_version jest Nic:
        sys_version = sys.version

    # Try the cache first
    result = _sys_version_cache.get(sys_version, Nic)
    jeżeli result jest nie Nic:
        zwróć result

    # Parse it
    jeżeli 'IronPython' w sys_version:
        # IronPython
        name = 'IronPython'
        jeżeli sys_version.startswith('IronPython'):
            match = _ironpython_sys_version_parser.match(sys_version)
        inaczej:
            match = _ironpython26_sys_version_parser.match(sys_version)

        jeżeli match jest Nic:
            podnieś ValueError(
                'failed to parse IronPython sys.version: %s' %
                repr(sys_version))

        version, alt_version, compiler = match.groups()
        buildno = ''
        builddate = ''

    albo_inaczej sys.platform.startswith('java'):
        # Jython
        name = 'Jython'
        match = _sys_version_parser.match(sys_version)
        jeżeli match jest Nic:
            podnieś ValueError(
                'failed to parse Jython sys.version: %s' %
                repr(sys_version))
        version, buildno, builddate, buildtime, _ = match.groups()
        compiler = sys.platform

    albo_inaczej "PyPy" w sys_version:
        # PyPy
        name = "PyPy"
        match = _pypy_sys_version_parser.match(sys_version)
        jeżeli match jest Nic:
            podnieś ValueError("failed to parse PyPy sys.version: %s" %
                             repr(sys_version))
        version, buildno, builddate, buildtime = match.groups()
        compiler = ""

    inaczej:
        # CPython
        match = _sys_version_parser.match(sys_version)
        jeżeli match jest Nic:
            podnieś ValueError(
                'failed to parse CPython sys.version: %s' %
                repr(sys_version))
        version, buildno, builddate, buildtime, compiler = \
              match.groups()
        name = 'CPython'
        builddate = builddate + ' ' + buildtime

    jeżeli hasattr(sys, '_mercurial'):
        _, branch, revision = sys._mercurial
    albo_inaczej hasattr(sys, 'subversion'):
        # sys.subversion was added w Python 2.5
        _, branch, revision = sys.subversion
    inaczej:
        branch = ''
        revision = ''

    # Add the patchlevel version jeżeli missing
    l = version.split('.')
    jeżeli len(l) == 2:
        l.append('0')
        version = '.'.join(l)

    # Build oraz cache the result
    result = (name, version, branch, revision, buildno, builddate, compiler)
    _sys_version_cache[sys_version] = result
    zwróć result

def python_implementation():

    """ Returns a string identifying the Python implementation.

        Currently, the following implementations are identified:
          'CPython' (C implementation of Python),
          'IronPython' (.NET implementation of Python),
          'Jython' (Java implementation of Python),
          'PyPy' (Python implementation of Python).

    """
    zwróć _sys_version()[0]

def python_version():

    """ Returns the Python version jako string 'major.minor.patchlevel'

        Note that unlike the Python sys.version, the returned value
        will always include the patchlevel (it defaults to 0).

    """
    zwróć _sys_version()[1]

def python_version_tuple():

    """ Returns the Python version jako tuple (major, minor, patchlevel)
        of strings.

        Note that unlike the Python sys.version, the returned value
        will always include the patchlevel (it defaults to 0).

    """
    zwróć tuple(_sys_version()[1].split('.'))

def python_branch():

    """ Returns a string identifying the Python implementation
        branch.

        For CPython this jest the Subversion branch z which the
        Python binary was built.

        If nie available, an empty string jest returned.

    """

    zwróć _sys_version()[2]

def python_revision():

    """ Returns a string identifying the Python implementation
        revision.

        For CPython this jest the Subversion revision z which the
        Python binary was built.

        If nie available, an empty string jest returned.

    """
    zwróć _sys_version()[3]

def python_build():

    """ Returns a tuple (buildno, builddate) stating the Python
        build number oraz date jako strings.

    """
    zwróć _sys_version()[4:6]

def python_compiler():

    """ Returns a string identifying the compiler used dla compiling
        Python.

    """
    zwróć _sys_version()[6]

### The Opus Magnum of platform strings :-)

_platform_cache = {}

def platform(aliased=0, terse=0):

    """ Returns a single string identifying the underlying platform
        przy jako much useful information jako possible (but no more :).

        The output jest intended to be human readable rather than
        machine parseable. It may look different on different
        platforms oraz this jest intended.

        If "aliased" jest true, the function will use aliases for
        various platforms that report system names which differ from
        their common names, e.g. SunOS will be reported as
        Solaris. The system_alias() function jest used to implement
        this.

        Setting terse to true causes the function to zwróć only the
        absolute minimum information needed to identify the platform.

    """
    result = _platform_cache.get((aliased, terse), Nic)
    jeżeli result jest nie Nic:
        zwróć result

    # Get uname information oraz then apply platform specific cosmetics
    # to it...
    system, node, release, version, machine, processor = uname()
    jeżeli machine == processor:
        processor = ''
    jeżeli aliased:
        system, release, version = system_alias(system, release, version)

    jeżeli system == 'Windows':
        # MS platforms
        rel, vers, csd, ptype = win32_ver(version)
        jeżeli terse:
            platform = _platform(system, release)
        inaczej:
            platform = _platform(system, release, version, csd)

    albo_inaczej system w ('Linux',):
        # Linux based systems
        przy warnings.catch_warnings():
            # see issue #1322 dla more information
            warnings.filterwarnings(
                'ignore',
                'dist\(\) oraz linux_distribution\(\) '
                'functions are deprecated .*',
                PendingDeprecationWarning,
            )
            distname, distversion, distid = dist('')
        jeżeli distname oraz nie terse:
            platform = _platform(system, release, machine, processor,
                                 'with',
                                 distname, distversion, distid)
        inaczej:
            # If the distribution name jest unknown check dla libc vs. glibc
            libcname, libcversion = libc_ver(sys.executable)
            platform = _platform(system, release, machine, processor,
                                 'with',
                                 libcname+libcversion)
    albo_inaczej system == 'Java':
        # Java platforms
        r, v, vminfo, (os_name, os_version, os_arch) = java_ver()
        jeżeli terse albo nie os_name:
            platform = _platform(system, release, version)
        inaczej:
            platform = _platform(system, release, version,
                                 'on',
                                 os_name, os_version, os_arch)

    albo_inaczej system == 'MacOS':
        # MacOS platforms
        jeżeli terse:
            platform = _platform(system, release)
        inaczej:
            platform = _platform(system, release, machine)

    inaczej:
        # Generic handler
        jeżeli terse:
            platform = _platform(system, release)
        inaczej:
            bits, linkage = architecture(sys.executable)
            platform = _platform(system, release, machine,
                                 processor, bits, linkage)

    _platform_cache[(aliased, terse)] = platform
    zwróć platform

### Command line interface

jeżeli __name__ == '__main__':
    # Default jest to print the aliased verbose platform string
    terse = ('terse' w sys.argv albo '--terse' w sys.argv)
    aliased = (nie 'nonaliased' w sys.argv oraz nie '--nonaliased' w sys.argv)
    print(platform(aliased, terse))
    sys.exit(0)
