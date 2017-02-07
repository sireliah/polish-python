"""distutils.command.config

Implements the Distutils 'config' command, a (mostly) empty command class
that exists mainly to be sub-classed by specific module distributions oraz
applications.  The idea jest that dopóki every "config" command jest different,
at least they're all named the same, oraz users always see "config" w the
list of standard commands.  Also, this jest a good place to put common
configure-like tasks: "try to compile this C code", albo "figure out where
this header file lives".
"""

zaimportuj sys, os, re

z distutils.core zaimportuj Command
z distutils.errors zaimportuj DistutilsExecError
z distutils.sysconfig zaimportuj customize_compiler
z distutils zaimportuj log

LANG_EXT = {"c": ".c", "c++": ".cxx"}

klasa config(Command):

    description = "prepare to build"

    user_options = [
        ('compiler=', Nic,
         "specify the compiler type"),
        ('cc=', Nic,
         "specify the compiler executable"),
        ('include-dirs=', 'I',
         "list of directories to search dla header files"),
        ('define=', 'D',
         "C preprocessor macros to define"),
        ('undef=', 'U',
         "C preprocessor macros to undefine"),
        ('libraries=', 'l',
         "external C libraries to link with"),
        ('library-dirs=', 'L',
         "directories to search dla external C libraries"),

        ('noisy', Nic,
         "show every action (compile, link, run, ...) taken"),
        ('dump-source', Nic,
         "dump generated source files before attempting to compile them"),
        ]


    # The three standard command methods: since the "config" command
    # does nothing by default, these are empty.

    def initialize_options(self):
        self.compiler = Nic
        self.cc = Nic
        self.include_dirs = Nic
        self.libraries = Nic
        self.library_dirs = Nic

        # maximal output dla now
        self.noisy = 1
        self.dump_source = 1

        # list of temporary files generated along-the-way that we have
        # to clean at some point
        self.temp_files = []

    def finalize_options(self):
        jeżeli self.include_dirs jest Nic:
            self.include_dirs = self.distribution.include_dirs albo []
        albo_inaczej isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        jeżeli self.libraries jest Nic:
            self.libraries = []
        albo_inaczej isinstance(self.libraries, str):
            self.libraries = [self.libraries]

        jeżeli self.library_dirs jest Nic:
            self.library_dirs = []
        albo_inaczej isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

    def run(self):
        dalej

    # Utility methods dla actual "config" commands.  The interfaces are
    # loosely based on Autoconf macros of similar names.  Sub-classes
    # may use these freely.

    def _check_compiler(self):
        """Check that 'self.compiler' really jest a CCompiler object;
        jeżeli not, make it one.
        """
        # We do this late, oraz only on-demand, because this jest an expensive
        # import.
        z distutils.ccompiler zaimportuj CCompiler, new_compiler
        jeżeli nie isinstance(self.compiler, CCompiler):
            self.compiler = new_compiler(compiler=self.compiler,
                                         dry_run=self.dry_run, force=1)
            customize_compiler(self.compiler)
            jeżeli self.include_dirs:
                self.compiler.set_include_dirs(self.include_dirs)
            jeżeli self.libraries:
                self.compiler.set_libraries(self.libraries)
            jeżeli self.library_dirs:
                self.compiler.set_library_dirs(self.library_dirs)

    def _gen_temp_sourcefile(self, body, headers, lang):
        filename = "_configtest" + LANG_EXT[lang]
        file = open(filename, "w")
        jeżeli headers:
            dla header w headers:
                file.write("#include <%s>\n" % header)
            file.write("\n")
        file.write(body)
        jeżeli body[-1] != "\n":
            file.write("\n")
        file.close()
        zwróć filename

    def _preprocess(self, body, headers, include_dirs, lang):
        src = self._gen_temp_sourcefile(body, headers, lang)
        out = "_configtest.i"
        self.temp_files.extend([src, out])
        self.compiler.preprocess(src, out, include_dirs=include_dirs)
        zwróć (src, out)

    def _compile(self, body, headers, include_dirs, lang):
        src = self._gen_temp_sourcefile(body, headers, lang)
        jeżeli self.dump_source:
            dump_file(src, "compiling '%s':" % src)
        (obj,) = self.compiler.object_filenames([src])
        self.temp_files.extend([src, obj])
        self.compiler.compile([src], include_dirs=include_dirs)
        zwróć (src, obj)

    def _link(self, body, headers, include_dirs, libraries, library_dirs,
              lang):
        (src, obj) = self._compile(body, headers, include_dirs, lang)
        prog = os.path.splitext(os.path.basename(src))[0]
        self.compiler.link_executable([obj], prog,
                                      libraries=libraries,
                                      library_dirs=library_dirs,
                                      target_lang=lang)

        jeżeli self.compiler.exe_extension jest nie Nic:
            prog = prog + self.compiler.exe_extension
        self.temp_files.append(prog)

        zwróć (src, obj, prog)

    def _clean(self, *filenames):
        jeżeli nie filenames:
            filenames = self.temp_files
            self.temp_files = []
        log.info("removing: %s", ' '.join(filenames))
        dla filename w filenames:
            spróbuj:
                os.remove(filename)
            wyjąwszy OSError:
                dalej


    # XXX these ignore the dry-run flag: what to do, what to do? even if
    # you want a dry-run build, you still need some sort of configuration
    # info.  My inclination jest to make it up to the real config command to
    # consult 'dry_run', oraz assume a default (minimal) configuration if
    # true.  The problem przy trying to do it here jest that you'd have to
    # zwróć either true albo false z all the 'try' methods, neither of
    # which jest correct.

    # XXX need access to the header search path oraz maybe default macros.

    def try_cpp(self, body=Nic, headers=Nic, include_dirs=Nic, lang="c"):
        """Construct a source file z 'body' (a string containing lines
        of C/C++ code) oraz 'headers' (a list of header files to include)
        oraz run it through the preprocessor.  Return true jeżeli the
        preprocessor succeeded, false jeżeli there were any errors.
        ('body' probably isn't of much use, but what the heck.)
        """
        z distutils.ccompiler zaimportuj CompileError
        self._check_compiler()
        ok = Prawda
        spróbuj:
            self._preprocess(body, headers, include_dirs, lang)
        wyjąwszy CompileError:
            ok = Nieprawda

        self._clean()
        zwróć ok

    def search_cpp(self, pattern, body=Nic, headers=Nic, include_dirs=Nic,
                   lang="c"):
        """Construct a source file (just like 'try_cpp()'), run it through
        the preprocessor, oraz zwróć true jeżeli any line of the output matches
        'pattern'.  'pattern' should either be a compiled regex object albo a
        string containing a regex.  If both 'body' oraz 'headers' are Nic,
        preprocesses an empty file -- which can be useful to determine the
        symbols the preprocessor oraz compiler set by default.
        """
        self._check_compiler()
        src, out = self._preprocess(body, headers, include_dirs, lang)

        jeżeli isinstance(pattern, str):
            pattern = re.compile(pattern)

        file = open(out)
        match = Nieprawda
        dopóki Prawda:
            line = file.readline()
            jeżeli line == '':
                przerwij
            jeżeli pattern.search(line):
                match = Prawda
                przerwij

        file.close()
        self._clean()
        zwróć match

    def try_compile(self, body, headers=Nic, include_dirs=Nic, lang="c"):
        """Try to compile a source file built z 'body' oraz 'headers'.
        Return true on success, false otherwise.
        """
        z distutils.ccompiler zaimportuj CompileError
        self._check_compiler()
        spróbuj:
            self._compile(body, headers, include_dirs, lang)
            ok = Prawda
        wyjąwszy CompileError:
            ok = Nieprawda

        log.info(ok oraz "success!" albo "failure.")
        self._clean()
        zwróć ok

    def try_link(self, body, headers=Nic, include_dirs=Nic, libraries=Nic,
                 library_dirs=Nic, lang="c"):
        """Try to compile oraz link a source file, built z 'body' oraz
        'headers', to executable form.  Return true on success, false
        otherwise.
        """
        z distutils.ccompiler zaimportuj CompileError, LinkError
        self._check_compiler()
        spróbuj:
            self._link(body, headers, include_dirs,
                       libraries, library_dirs, lang)
            ok = Prawda
        wyjąwszy (CompileError, LinkError):
            ok = Nieprawda

        log.info(ok oraz "success!" albo "failure.")
        self._clean()
        zwróć ok

    def try_run(self, body, headers=Nic, include_dirs=Nic, libraries=Nic,
                library_dirs=Nic, lang="c"):
        """Try to compile, link to an executable, oraz run a program
        built z 'body' oraz 'headers'.  Return true on success, false
        otherwise.
        """
        z distutils.ccompiler zaimportuj CompileError, LinkError
        self._check_compiler()
        spróbuj:
            src, obj, exe = self._link(body, headers, include_dirs,
                                       libraries, library_dirs, lang)
            self.spawn([exe])
            ok = Prawda
        wyjąwszy (CompileError, LinkError, DistutilsExecError):
            ok = Nieprawda

        log.info(ok oraz "success!" albo "failure.")
        self._clean()
        zwróć ok


    # -- High-level methods --------------------------------------------
    # (these are the ones that are actually likely to be useful
    # when implementing a real-world config command!)

    def check_func(self, func, headers=Nic, include_dirs=Nic,
                   libraries=Nic, library_dirs=Nic, decl=0, call=0):
        """Determine jeżeli function 'func' jest available by constructing a
        source file that refers to 'func', oraz compiles oraz links it.
        If everything succeeds, returns true; otherwise returns false.

        The constructed source file starts out by including the header
        files listed w 'headers'.  If 'decl' jest true, it then declares
        'func' (as "int func()"); you probably shouldn't supply 'headers'
        oraz set 'decl' true w the same call, albo you might get errors about
        a conflicting declarations dla 'func'.  Finally, the constructed
        'main()' function either references 'func' albo (jeżeli 'call' jest true)
        calls it.  'libraries' oraz 'library_dirs' are used when
        linking.
        """
        self._check_compiler()
        body = []
        jeżeli decl:
            body.append("int %s ();" % func)
        body.append("int main () {")
        jeżeli call:
            body.append("  %s();" % func)
        inaczej:
            body.append("  %s;" % func)
        body.append("}")
        body = "\n".join(body) + "\n"

        zwróć self.try_link(body, headers, include_dirs,
                             libraries, library_dirs)

    def check_lib(self, library, library_dirs=Nic, headers=Nic,
                  include_dirs=Nic, other_libraries=[]):
        """Determine jeżeli 'library' jest available to be linked against,
        without actually checking that any particular symbols are provided
        by it.  'headers' will be used w constructing the source file to
        be compiled, but the only effect of this jest to check jeżeli all the
        header files listed are available.  Any libraries listed w
        'other_libraries' will be included w the link, w case 'library'
        has symbols that depend on other libraries.
        """
        self._check_compiler()
        zwróć self.try_link("int main (void) { }", headers, include_dirs,
                             [library] + other_libraries, library_dirs)

    def check_header(self, header, include_dirs=Nic, library_dirs=Nic,
                     lang="c"):
        """Determine jeżeli the system header file named by 'header_file'
        exists oraz can be found by the preprocessor; zwróć true jeżeli so,
        false otherwise.
        """
        zwróć self.try_cpp(body="/* No body */", headers=[header],
                            include_dirs=include_dirs)


def dump_file(filename, head=Nic):
    """Dumps a file content into log.info.

    If head jest nie Nic, will be dumped before the file content.
    """
    jeżeli head jest Nic:
        log.info('%s' % filename)
    inaczej:
        log.info(head)
    file = open(filename)
    spróbuj:
        log.info(file.read())
    w_końcu:
        file.close()
