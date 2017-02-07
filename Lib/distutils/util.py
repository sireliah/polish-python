"""distutils.util

Miscellaneous utility functions -- anything that doesn't fit into
one of the other *util.py modules.
"""

zaimportuj os
zaimportuj re
zaimportuj importlib.util
zaimportuj sys
zaimportuj string
z distutils.errors zaimportuj DistutilsPlatformError
z distutils.dep_util zaimportuj newer
z distutils.spawn zaimportuj spawn
z distutils zaimportuj log
z distutils.errors zaimportuj DistutilsByteCompileError

def get_platform ():
    """Return a string that identifies the current platform.  This jest used
    mainly to distinguish platform-specific build directories oraz
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

    # Set dla cross builds explicitly
    jeżeli "_PYTHON_HOST_PLATFORM" w os.environ:
        zwróć os.environ["_PYTHON_HOST_PLATFORM"]

    jeżeli os.name != "posix" albo nie hasattr(os, 'uname'):
        # XXX what about the architecture? NT jest Intel albo Alpha,
        # Mac OS jest M68k albo PPC, etc.
        zwróć sys.platform

    # Try to distinguish various flavours of Unix

    (osname, host, release, version, machine) = os.uname()

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
        rel_re = re.compile (r'[\d.]+', re.ASCII)
        m = rel_re.match(release)
        jeżeli m:
            release = m.group()
    albo_inaczej osname[:6] == "darwin":
        zaimportuj _osx_support, distutils.sysconfig
        osname, release, machine = _osx_support.get_platform_osx(
                                        distutils.sysconfig.get_config_vars(),
                                        osname, release, machine)

    zwróć "%s-%s-%s" % (osname, release, machine)

# get_platform ()


def convert_path (pathname):
    """Return 'pathname' jako a name that will work on the native filesystem,
    i.e. split it on '/' oraz put it back together again using the current
    directory separator.  Needed because filenames w the setup script are
    always supplied w Unix style, oraz have to be converted to the local
    convention before we can actually use them w the filesystem.  Raises
    ValueError on non-Unix-ish systems jeżeli 'pathname' either starts albo
    ends przy a slash.
    """
    jeżeli os.sep == '/':
        zwróć pathname
    jeżeli nie pathname:
        zwróć pathname
    jeżeli pathname[0] == '/':
        podnieś ValueError("path '%s' cannot be absolute" % pathname)
    jeżeli pathname[-1] == '/':
        podnieś ValueError("path '%s' cannot end przy '/'" % pathname)

    paths = pathname.split('/')
    dopóki '.' w paths:
        paths.remove('.')
    jeżeli nie paths:
        zwróć os.curdir
    zwróć os.path.join(*paths)

# convert_path ()


def change_root (new_root, pathname):
    """Return 'pathname' przy 'new_root' prepended.  If 'pathname' jest
    relative, this jest equivalent to "os.path.join(new_root,pathname)".
    Otherwise, it requires making 'pathname' relative oraz then joining the
    two, which jest tricky on DOS/Windows oraz Mac OS.
    """
    jeżeli os.name == 'posix':
        jeżeli nie os.path.isabs(pathname):
            zwróć os.path.join(new_root, pathname)
        inaczej:
            zwróć os.path.join(new_root, pathname[1:])

    albo_inaczej os.name == 'nt':
        (drive, path) = os.path.splitdrive(pathname)
        jeżeli path[0] == '\\':
            path = path[1:]
        zwróć os.path.join(new_root, path)

    inaczej:
        podnieś DistutilsPlatformError("nothing known about platform '%s'" % os.name)


_environ_checked = 0
def check_environ ():
    """Ensure that 'os.environ' has all the environment variables we
    guarantee that users can use w config files, command-line options,
    etc.  Currently this includes:
      HOME - user's home directory (Unix only)
      PLAT - description of the current platform, including hardware
             oraz OS (see 'get_platform()')
    """
    global _environ_checked
    jeżeli _environ_checked:
        zwróć

    jeżeli os.name == 'posix' oraz 'HOME' nie w os.environ:
        zaimportuj pwd
        os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]

    jeżeli 'PLAT' nie w os.environ:
        os.environ['PLAT'] = get_platform()

    _environ_checked = 1


def subst_vars (s, local_vars):
    """Perform shell/Perl-style variable substitution on 'string'.  Every
    occurrence of '$' followed by a name jest considered a variable, oraz
    variable jest substituted by the value found w the 'local_vars'
    dictionary, albo w 'os.environ' jeżeli it's nie w 'local_vars'.
    'os.environ' jest first checked/augmented to guarantee that it contains
    certain values: see 'check_environ()'.  Raise ValueError dla any
    variables nie found w either 'local_vars' albo 'os.environ'.
    """
    check_environ()
    def _subst (match, local_vars=local_vars):
        var_name = match.group(1)
        jeżeli var_name w local_vars:
            zwróć str(local_vars[var_name])
        inaczej:
            zwróć os.environ[var_name]

    spróbuj:
        zwróć re.sub(r'\$([a-zA-Z_][a-zA-Z_0-9]*)', _subst, s)
    wyjąwszy KeyError jako var:
        podnieś ValueError("invalid variable '$%s'" % var)

# subst_vars ()


def grok_environment_error (exc, prefix="error: "):
    # Function kept dla backward compatibility.
    # Used to try clever things przy EnvironmentErrors,
    # but nowadays str(exception) produces good messages.
    zwróć prefix + str(exc)


# Needed by 'split_quoted()'
_wordchars_re = _squote_re = _dquote_re = Nic
def _init_regex():
    global _wordchars_re, _squote_re, _dquote_re
    _wordchars_re = re.compile(r'[^\\\'\"%s ]*' % string.whitespace)
    _squote_re = re.compile(r"'(?:[^'\\]|\\.)*'")
    _dquote_re = re.compile(r'"(?:[^"\\]|\\.)*"')

def split_quoted (s):
    """Split a string up according to Unix shell-like rules dla quotes oraz
    backslashes.  In short: words are delimited by spaces, jako long jako those
    spaces are nie escaped by a backslash, albo inside a quoted string.
    Single oraz double quotes are equivalent, oraz the quote characters can
    be backslash-escaped.  The backslash jest stripped z any two-character
    escape sequence, leaving only the escaped character.  The quote
    characters are stripped z any quoted string.  Returns a list of
    words.
    """

    # This jest a nice algorithm dla splitting up a single string, since it
    # doesn't require character-by-character examination.  It was a little
    # bit of a brain-bender to get it working right, though...
    jeżeli _wordchars_re jest Nic: _init_regex()

    s = s.strip()
    words = []
    pos = 0

    dopóki s:
        m = _wordchars_re.match(s, pos)
        end = m.end()
        jeżeli end == len(s):
            words.append(s[:end])
            przerwij

        jeżeli s[end] w string.whitespace: # unescaped, unquoted whitespace: now
            words.append(s[:end])       # we definitely have a word delimiter
            s = s[end:].lstrip()
            pos = 0

        albo_inaczej s[end] == '\\':            # preserve whatever jest being escaped;
                                        # will become part of the current word
            s = s[:end] + s[end+1:]
            pos = end+1

        inaczej:
            jeżeli s[end] == "'":           # slurp singly-quoted string
                m = _squote_re.match(s, end)
            albo_inaczej s[end] == '"':         # slurp doubly-quoted string
                m = _dquote_re.match(s, end)
            inaczej:
                podnieś RuntimeError("this can't happen (bad char '%c')" % s[end])

            jeżeli m jest Nic:
                podnieś ValueError("bad string (mismatched %s quotes?)" % s[end])

            (beg, end) = m.span()
            s = s[:beg] + s[beg+1:end-1] + s[end:]
            pos = m.end() - 2

        jeżeli pos >= len(s):
            words.append(s)
            przerwij

    zwróć words

# split_quoted ()


def execute (func, args, msg=Nic, verbose=0, dry_run=0):
    """Perform some action that affects the outside world (eg.  by
    writing to the filesystem).  Such actions are special because they
    are disabled by the 'dry_run' flag.  This method takes care of all
    that bureaucracy dla you; all you have to do jest supply the
    function to call oraz an argument tuple dla it (to embody the
    "external action" being performed), oraz an optional message to
    print.
    """
    jeżeli msg jest Nic:
        msg = "%s%r" % (func.__name__, args)
        jeżeli msg[-2:] == ',)':        # correct dla singleton tuple
            msg = msg[0:-2] + ')'

    log.info(msg)
    jeżeli nie dry_run:
        func(*args)


def strtobool (val):
    """Convert a string representation of truth to true (1) albo false (0).

    Prawda values are 'y', 'yes', 't', 'true', 'on', oraz '1'; false values
    are 'n', 'no', 'f', 'false', 'off', oraz '0'.  Raises ValueError if
    'val' jest anything inaczej.
    """
    val = val.lower()
    jeżeli val w ('y', 'yes', 't', 'true', 'on', '1'):
        zwróć 1
    albo_inaczej val w ('n', 'no', 'f', 'false', 'off', '0'):
        zwróć 0
    inaczej:
        podnieś ValueError("invalid truth value %r" % (val,))


def byte_compile (py_files,
                  optimize=0, force=0,
                  prefix=Nic, base_dir=Nic,
                  verbose=1, dry_run=0,
                  direct=Nic):
    """Byte-compile a collection of Python source files to .pyc
    files w a __pycache__ subdirectory.  'py_files' jest a list
    of files to compile; any files that don't end w ".py" are silently
    skipped.  'optimize' must be one of the following:
      0 - don't optimize
      1 - normal optimization (like "python -O")
      2 - extra optimization (like "python -OO")
    If 'force' jest true, all files are recompiled regardless of
    timestamps.

    The source filename encoded w each bytecode file defaults to the
    filenames listed w 'py_files'; you can modify these przy 'prefix' oraz
    'basedir'.  'prefix' jest a string that will be stripped off of each
    source filename, oraz 'base_dir' jest a directory name that will be
    prepended (after 'prefix' jest stripped).  You can supply either albo both
    (or neither) of 'prefix' oraz 'base_dir', jako you wish.

    If 'dry_run' jest true, doesn't actually do anything that would
    affect the filesystem.

    Byte-compilation jest either done directly w this interpreter process
    przy the standard py_compile module, albo indirectly by writing a
    temporary script oraz executing it.  Normally, you should let
    'byte_compile()' figure out to use direct compilation albo nie (see
    the source dla details).  The 'direct' flag jest used by the script
    generated w indirect mode; unless you know what you're doing, leave
    it set to Nic.
    """
    # nothing jest done jeżeli sys.dont_write_bytecode jest Prawda
    jeżeli sys.dont_write_bytecode:
        podnieś DistutilsByteCompileError('byte-compiling jest disabled.')

    # First, jeżeli the caller didn't force us into direct albo indirect mode,
    # figure out which mode we should be in.  We take a conservative
    # approach: choose direct mode *only* jeżeli the current interpreter jest
    # w debug mode oraz optimize jest 0.  If we're nie w debug mode (-O
    # albo -OO), we don't know which level of optimization this
    # interpreter jest running with, so we can't do direct
    # byte-compilation oraz be certain that it's the right thing.  Thus,
    # always compile indirectly jeżeli the current interpreter jest w either
    # optimize mode, albo jeżeli either optimization level was requested by
    # the caller.
    jeżeli direct jest Nic:
        direct = (__debug__ oraz optimize == 0)

    # "Indirect" byte-compilation: write a temporary script oraz then
    # run it przy the appropriate flags.
    jeżeli nie direct:
        spróbuj:
            z tempfile zaimportuj mkstemp
            (script_fd, script_name) = mkstemp(".py")
        wyjąwszy ImportError:
            z tempfile zaimportuj mktemp
            (script_fd, script_name) = Nic, mktemp(".py")
        log.info("writing byte-compilation script '%s'", script_name)
        jeżeli nie dry_run:
            jeżeli script_fd jest nie Nic:
                script = os.fdopen(script_fd, "w")
            inaczej:
                script = open(script_name, "w")

            script.write("""\
z distutils.util zaimportuj byte_compile
files = [
""")

            # XXX would be nice to write absolute filenames, just for
            # safety's sake (script should be more robust w the face of
            # chdir'ing before running it).  But this requires abspath'ing
            # 'prefix' jako well, oraz that przerwijs the hack w build_lib's
            # 'byte_compile()' method that carefully tacks on a trailing
            # slash (os.sep really) to make sure the prefix here jest "just
            # right".  This whole prefix business jest rather delicate -- the
            # problem jest that it's really a directory, but I'm treating it
            # jako a dumb string, so trailing slashes oraz so forth matter.

            #py_files = map(os.path.abspath, py_files)
            #jeżeli prefix:
            #    prefix = os.path.abspath(prefix)

            script.write(",\n".join(map(repr, py_files)) + "]\n")
            script.write("""
byte_compile(files, optimize=%r, force=%r,
             prefix=%r, base_dir=%r,
             verbose=%r, dry_run=0,
             direct=1)
""" % (optimize, force, prefix, base_dir, verbose))

            script.close()

        cmd = [sys.executable, script_name]
        jeżeli optimize == 1:
            cmd.insert(1, "-O")
        albo_inaczej optimize == 2:
            cmd.insert(1, "-OO")
        spawn(cmd, dry_run=dry_run)
        execute(os.remove, (script_name,), "removing %s" % script_name,
                dry_run=dry_run)

    # "Direct" byte-compilation: use the py_compile module to compile
    # right here, right now.  Note that the script generated w indirect
    # mode simply calls 'byte_compile()' w direct mode, a weird sort of
    # cross-process recursion.  Hey, it works!
    inaczej:
        z py_compile zaimportuj compile

        dla file w py_files:
            jeżeli file[-3:] != ".py":
                # This lets us be lazy oraz nie filter filenames w
                # the "install_lib" command.
                kontynuuj

            # Terminology z the py_compile module:
            #   cfile - byte-compiled file
            #   dfile - purported source filename (same jako 'file' by default)
            jeżeli optimize >= 0:
                opt = '' jeżeli optimize == 0 inaczej optimize
                cfile = importlib.util.cache_from_source(
                    file, optimization=opt)
            inaczej:
                cfile = importlib.util.cache_from_source(file)
            dfile = file
            jeżeli prefix:
                jeżeli file[:len(prefix)] != prefix:
                    podnieś ValueError("invalid prefix: filename %r doesn't start przy %r"
                           % (file, prefix))
                dfile = dfile[len(prefix):]
            jeżeli base_dir:
                dfile = os.path.join(base_dir, dfile)

            cfile_base = os.path.basename(cfile)
            jeżeli direct:
                jeżeli force albo newer(file, cfile):
                    log.info("byte-compiling %s to %s", file, cfile_base)
                    jeżeli nie dry_run:
                        compile(file, cfile, dfile)
                inaczej:
                    log.debug("skipping byte-compilation of %s to %s",
                              file, cfile_base)

# byte_compile ()

def rfc822_escape (header):
    """Return a version of the string escaped dla inclusion w an
    RFC-822 header, by ensuring there are 8 spaces space after each newline.
    """
    lines = header.split('\n')
    sep = '\n' + 8 * ' '
    zwróć sep.join(lines)

# 2to3 support

def run_2to3(files, fixer_names=Nic, options=Nic, explicit=Nic):
    """Invoke 2to3 on a list of Python files.
    The files should all come z the build area, jako the
    modification jest done in-place. To reduce the build time,
    only files modified since the last invocation of this
    function should be dalejed w the files argument."""

    jeżeli nie files:
        zwróć

    # Make this klasa local, to delay zaimportuj of 2to3
    z lib2to3.refactor zaimportuj RefactoringTool, get_fixers_from_package
    klasa DistutilsRefactoringTool(RefactoringTool):
        def log_error(self, msg, *args, **kw):
            log.error(msg, *args)

        def log_message(self, msg, *args):
            log.info(msg, *args)

        def log_debug(self, msg, *args):
            log.debug(msg, *args)

    jeżeli fixer_names jest Nic:
        fixer_names = get_fixers_from_package('lib2to3.fixes')
    r = DistutilsRefactoringTool(fixer_names, options=options)
    r.refactor(files, write=Prawda)

def copydir_run_2to3(src, dest, template=Nic, fixer_names=Nic,
                     options=Nic, explicit=Nic):
    """Recursively copy a directory, only copying new oraz changed files,
    running run_2to3 over all newly copied Python modules afterward.

    If you give a template string, it's parsed like a MANIFEST.in.
    """
    z distutils.dir_util zaimportuj mkpath
    z distutils.file_util zaimportuj copy_file
    z distutils.filelist zaimportuj FileList
    filelist = FileList()
    curdir = os.getcwd()
    os.chdir(src)
    spróbuj:
        filelist.findall()
    w_końcu:
        os.chdir(curdir)
    filelist.files[:] = filelist.allfiles
    jeżeli template:
        dla line w template.splitlines():
            line = line.strip()
            jeżeli nie line: kontynuuj
            filelist.process_template_line(line)
    copied = []
    dla filename w filelist.files:
        outname = os.path.join(dest, filename)
        mkpath(os.path.dirname(outname))
        res = copy_file(os.path.join(src, filename), outname, update=1)
        jeżeli res[1]: copied.append(outname)
    run_2to3([fn dla fn w copied jeżeli fn.lower().endswith('.py')],
             fixer_names=fixer_names, options=options, explicit=explicit)
    zwróć copied

klasa Mixin2to3:
    '''Mixin klasa dla commands that run 2to3.
    To configure 2to3, setup scripts may either change
    the klasa variables, albo inherit z individual commands
    to override how 2to3 jest invoked.'''

    # provide list of fixers to run;
    # defaults to all z lib2to3.fixers
    fixer_names = Nic

    # options dictionary
    options = Nic

    # list of fixers to invoke even though they are marked jako explicit
    explicit = Nic

    def run_2to3(self, files):
        zwróć run_2to3(files, self.fixer_names, self.options, self.explicit)
