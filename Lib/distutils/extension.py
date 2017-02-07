"""distutils.extension

Provides the Extension class, used to describe C/C++ extension
modules w setup scripts."""

zaimportuj os
zaimportuj sys
zaimportuj warnings

# This klasa jest really only used by the "build_ext" command, so it might
# make sense to put it w distutils.command.build_ext.  However, that
# module jest already big enough, oraz I want to make this klasa a bit more
# complex to simplify some common cases ("foo" module w "foo.c") oraz do
# better error-checking ("foo.c" actually exists).
#
# Also, putting this w build_ext.py means every setup script would have to
# zaimportuj that large-ish module (indirectly, through distutils.core) w
# order to do anything.

klasa Extension:
    """Just a collection of attributes that describes an extension
    module oraz everything needed to build it (hopefully w a portable
    way, but there are hooks that let you be jako unportable jako you need).

    Instance attributes:
      name : string
        the full name of the extension, including any packages -- ie.
        *not* a filename albo pathname, but Python dotted name
      sources : [string]
        list of source filenames, relative to the distribution root
        (where the setup script lives), w Unix form (slash-separated)
        dla portability.  Source files may be C, C++, SWIG (.i),
        platform-specific resource files, albo whatever inaczej jest recognized
        by the "build_ext" command jako source dla a Python extension.
      include_dirs : [string]
        list of directories to search dla C/C++ header files (in Unix
        form dla portability)
      define_macros : [(name : string, value : string|Nic)]
        list of macros to define; each macro jest defined using a 2-tuple,
        where 'value' jest either the string to define it to albo Nic to
        define it without a particular value (equivalent of "#define
        FOO" w source albo -DFOO on Unix C compiler command line)
      undef_macros : [string]
        list of macros to undefine explicitly
      library_dirs : [string]
        list of directories to search dla C/C++ libraries at link time
      libraries : [string]
        list of library names (nie filenames albo paths) to link against
      runtime_library_dirs : [string]
        list of directories to search dla C/C++ libraries at run time
        (dla shared extensions, this jest when the extension jest loaded)
      extra_objects : [string]
        list of extra files to link przy (eg. object files nie implied
        by 'sources', static library that must be explicitly specified,
        binary resource files, etc.)
      extra_compile_args : [string]
        any extra platform- oraz compiler-specific information to use
        when compiling the source files w 'sources'.  For platforms oraz
        compilers where "command line" makes sense, this jest typically a
        list of command-line arguments, but dla other platforms it could
        be anything.
      extra_link_args : [string]
        any extra platform- oraz compiler-specific information to use
        when linking object files together to create the extension (or
        to create a new static Python interpreter).  Similar
        interpretation jako dla 'extra_compile_args'.
      export_symbols : [string]
        list of symbols to be exported z a shared extension.  Not
        used on all platforms, oraz nie generally necessary dla Python
        extensions, which typically export exactly one symbol: "init" +
        extension_name.
      swig_opts : [string]
        any extra options to dalej to SWIG jeżeli a source file has the .i
        extension.
      depends : [string]
        list of files that the extension depends on
      language : string
        extension language (i.e. "c", "c++", "objc"). Will be detected
        z the source extensions jeżeli nie provided.
      optional : boolean
        specifies that a build failure w the extension should nie abort the
        build process, but simply nie install the failing extension.
    """

    # When adding arguments to this constructor, be sure to update
    # setup_keywords w core.py.
    def __init__(self, name, sources,
                  include_dirs=Nic,
                  define_macros=Nic,
                  undef_macros=Nic,
                  library_dirs=Nic,
                  libraries=Nic,
                  runtime_library_dirs=Nic,
                  extra_objects=Nic,
                  extra_compile_args=Nic,
                  extra_link_args=Nic,
                  export_symbols=Nic,
                  swig_opts = Nic,
                  depends=Nic,
                  language=Nic,
                  optional=Nic,
                  **kw                      # To catch unknown keywords
                 ):
        jeżeli nie isinstance(name, str):
            podnieś AssertionError("'name' must be a string")
        jeżeli nie (isinstance(sources, list) oraz
                all(isinstance(v, str) dla v w sources)):
            podnieś AssertionError("'sources' must be a list of strings")

        self.name = name
        self.sources = sources
        self.include_dirs = include_dirs albo []
        self.define_macros = define_macros albo []
        self.undef_macros = undef_macros albo []
        self.library_dirs = library_dirs albo []
        self.libraries = libraries albo []
        self.runtime_library_dirs = runtime_library_dirs albo []
        self.extra_objects = extra_objects albo []
        self.extra_compile_args = extra_compile_args albo []
        self.extra_link_args = extra_link_args albo []
        self.export_symbols = export_symbols albo []
        self.swig_opts = swig_opts albo []
        self.depends = depends albo []
        self.language = language
        self.optional = optional

        # If there are unknown keyword options, warn about them
        jeżeli len(kw) > 0:
            options = [repr(option) dla option w kw]
            options = ', '.join(sorted(options))
            msg = "Unknown Extension options: %s" % options
            warnings.warn(msg)

    def __repr__(self):
        zwróć '<%s.%s(%r) at %#x>' % (
            self.__class__.__module__,
            self.__class__.__qualname__,
            self.name,
            id(self))


def read_setup_file(filename):
    """Reads a Setup file oraz returns Extension instances."""
    z distutils.sysconfig zaimportuj (parse_makefile, expand_makefile_vars,
                                     _variable_rx)

    z distutils.text_file zaimportuj TextFile
    z distutils.util zaimportuj split_quoted

    # First dalej over the file to gather "VAR = VALUE" assignments.
    vars = parse_makefile(filename)

    # Second dalej to gobble up the real content: lines of the form
    #   <module> ... [<sourcefile> ...] [<cpparg> ...] [<library> ...]
    file = TextFile(filename,
                    strip_comments=1, skip_blanks=1, join_lines=1,
                    lstrip_ws=1, rstrip_ws=1)
    spróbuj:
        extensions = []

        dopóki Prawda:
            line = file.readline()
            jeżeli line jest Nic:                # eof
                przerwij
            jeżeli _variable_rx.match(line):    # VAR=VALUE, handled w first dalej
                kontynuuj

            jeżeli line[0] == line[-1] == "*":
                file.warn("'%s' lines nie handled yet" % line)
                kontynuuj

            line = expand_makefile_vars(line, vars)
            words = split_quoted(line)

            # NB. this parses a slightly different syntax than the old
            # makesetup script: here, there must be exactly one extension per
            # line, oraz it must be the first word of the line.  I have no idea
            # why the old syntax supported multiple extensions per line, as
            # they all wind up being the same.

            module = words[0]
            ext = Extension(module, [])
            append_next_word = Nic

            dla word w words[1:]:
                jeżeli append_next_word jest nie Nic:
                    append_next_word.append(word)
                    append_next_word = Nic
                    kontynuuj

                suffix = os.path.splitext(word)[1]
                switch = word[0:2] ; value = word[2:]

                jeżeli suffix w (".c", ".cc", ".cpp", ".cxx", ".c++", ".m", ".mm"):
                    # hmm, should we do something about C vs. C++ sources?
                    # albo leave it up to the CCompiler implementation to
                    # worry about?
                    ext.sources.append(word)
                albo_inaczej switch == "-I":
                    ext.include_dirs.append(value)
                albo_inaczej switch == "-D":
                    equals = value.find("=")
                    jeżeli equals == -1:        # bare "-DFOO" -- no value
                        ext.define_macros.append((value, Nic))
                    inaczej:                   # "-DFOO=blah"
                        ext.define_macros.append((value[0:equals],
                                                  value[equals+2:]))
                albo_inaczej switch == "-U":
                    ext.undef_macros.append(value)
                albo_inaczej switch == "-C":        # only here 'cause makesetup has it!
                    ext.extra_compile_args.append(word)
                albo_inaczej switch == "-l":
                    ext.libraries.append(value)
                albo_inaczej switch == "-L":
                    ext.library_dirs.append(value)
                albo_inaczej switch == "-R":
                    ext.runtime_library_dirs.append(value)
                albo_inaczej word == "-rpath":
                    append_next_word = ext.runtime_library_dirs
                albo_inaczej word == "-Xlinker":
                    append_next_word = ext.extra_link_args
                albo_inaczej word == "-Xcompiler":
                    append_next_word = ext.extra_compile_args
                albo_inaczej switch == "-u":
                    ext.extra_link_args.append(word)
                    jeżeli nie value:
                        append_next_word = ext.extra_link_args
                albo_inaczej suffix w (".a", ".so", ".sl", ".o", ".dylib"):
                    # NB. a really faithful emulation of makesetup would
                    # append a .o file to extra_objects only jeżeli it
                    # had a slash w it; otherwise, it would s/.o/.c/
                    # oraz append it to sources.  Hmmmm.
                    ext.extra_objects.append(word)
                inaczej:
                    file.warn("unrecognized argument '%s'" % word)

            extensions.append(ext)
    w_końcu:
        file.close()

    zwróć extensions
