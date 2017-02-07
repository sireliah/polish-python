"""distutils.command.build_py

Implements the Distutils 'build_py' command."""

zaimportuj os
zaimportuj importlib.util
zaimportuj sys
z glob zaimportuj glob

z distutils.core zaimportuj Command
z distutils.errors zaimportuj *
z distutils.util zaimportuj convert_path, Mixin2to3
z distutils zaimportuj log

klasa build_py (Command):

    description = "\"build\" pure Python modules (copy to build directory)"

    user_options = [
        ('build-lib=', 'd', "directory to \"build\" (copy) to"),
        ('compile', 'c', "compile .py to .pyc"),
        ('no-compile', Nic, "don't compile .py files [default]"),
        ('optimize=', 'O',
         "also compile przy optimization: -O1 dla \"python -O\", "
         "-O2 dla \"python -OO\", oraz -O0 to disable [default: -O0]"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
        ]

    boolean_options = ['compile', 'force']
    negative_opt = {'no-compile' : 'compile'}

    def initialize_options(self):
        self.build_lib = Nic
        self.py_modules = Nic
        self.package = Nic
        self.package_data = Nic
        self.package_dir = Nic
        self.compile = 0
        self.optimize = 0
        self.force = Nic

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('force', 'force'))

        # Get the distribution options that are aliases dla build_py
        # options -- list of packages oraz list of modules.
        self.packages = self.distribution.packages
        self.py_modules = self.distribution.py_modules
        self.package_data = self.distribution.package_data
        self.package_dir = {}
        jeżeli self.distribution.package_dir:
            dla name, path w self.distribution.package_dir.items():
                self.package_dir[name] = convert_path(path)
        self.data_files = self.get_data_files()

        # Ick, copied straight z install_lib.py (fancy_getopt needs a
        # type system!  Hell, *everything* needs a type system!!!)
        jeżeli nie isinstance(self.optimize, int):
            spróbuj:
                self.optimize = int(self.optimize)
                assert 0 <= self.optimize <= 2
            wyjąwszy (ValueError, AssertionError):
                podnieś DistutilsOptionError("optimize must be 0, 1, albo 2")

    def run(self):
        # XXX copy_file by default preserves atime oraz mtime.  IMHO this jest
        # the right thing to do, but perhaps it should be an option -- w
        # particular, a site administrator might want installed files to
        # reflect the time of installation rather than the last
        # modification time before the installed release.

        # XXX copy_file by default preserves mode, which appears to be the
        # wrong thing to do: jeżeli a file jest read-only w the working
        # directory, we want it to be installed read/write so that the next
        # installation of the same module distribution can overwrite it
        # without problems.  (This might be a Unix-specific issue.)  Thus
        # we turn off 'preserve_mode' when copying to the build directory,
        # since the build directory jest supposed to be exactly what the
        # installation will look like (ie. we preserve mode when
        # installing).

        # Two options control which modules will be installed: 'packages'
        # oraz 'py_modules'.  The former lets us work przy whole packages, nie
        # specifying individual modules at all; the latter jest for
        # specifying modules one-at-a-time.

        jeżeli self.py_modules:
            self.build_modules()
        jeżeli self.packages:
            self.build_packages()
            self.build_package_data()

        self.byte_compile(self.get_outputs(include_bytecode=0))

    def get_data_files(self):
        """Generate list of '(package,src_dir,build_dir,filenames)' tuples"""
        data = []
        jeżeli nie self.packages:
            zwróć data
        dla package w self.packages:
            # Locate package source directory
            src_dir = self.get_package_dir(package)

            # Compute package build directory
            build_dir = os.path.join(*([self.build_lib] + package.split('.')))

            # Length of path to strip z found files
            plen = 0
            jeżeli src_dir:
                plen = len(src_dir)+1

            # Strip directory z globbed filenames
            filenames = [
                file[plen:] dla file w self.find_data_files(package, src_dir)
                ]
            data.append((package, src_dir, build_dir, filenames))
        zwróć data

    def find_data_files(self, package, src_dir):
        """Return filenames dla package's data files w 'src_dir'"""
        globs = (self.package_data.get('', [])
                 + self.package_data.get(package, []))
        files = []
        dla pattern w globs:
            # Each pattern has to be converted to a platform-specific path
            filelist = glob(os.path.join(src_dir, convert_path(pattern)))
            # Files that match more than one pattern are only added once
            files.extend([fn dla fn w filelist jeżeli fn nie w files
                oraz os.path.isfile(fn)])
        zwróć files

    def build_package_data(self):
        """Copy data files into build directory"""
        lastdir = Nic
        dla package, src_dir, build_dir, filenames w self.data_files:
            dla filename w filenames:
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                self.copy_file(os.path.join(src_dir, filename), target,
                               preserve_mode=Nieprawda)

    def get_package_dir(self, package):
        """Return the directory, relative to the top of the source
           distribution, where package 'package' should be found
           (at least according to the 'package_dir' option, jeżeli any)."""
        path = package.split('.')

        jeżeli nie self.package_dir:
            jeżeli path:
                zwróć os.path.join(*path)
            inaczej:
                zwróć ''
        inaczej:
            tail = []
            dopóki path:
                spróbuj:
                    pdir = self.package_dir['.'.join(path)]
                wyjąwszy KeyError:
                    tail.insert(0, path[-1])
                    usuń path[-1]
                inaczej:
                    tail.insert(0, pdir)
                    zwróć os.path.join(*tail)
            inaczej:
                # Oops, got all the way through 'path' without finding a
                # match w package_dir.  If package_dir defines a directory
                # dla the root (nameless) package, then fallback on it;
                # otherwise, we might jako well have nie consulted
                # package_dir at all, jako we just use the directory implied
                # by 'tail' (which should be the same jako the original value
                # of 'path' at this point).
                pdir = self.package_dir.get('')
                jeżeli pdir jest nie Nic:
                    tail.insert(0, pdir)

                jeżeli tail:
                    zwróć os.path.join(*tail)
                inaczej:
                    zwróć ''

    def check_package(self, package, package_dir):
        # Empty dir name means current directory, which we can probably
        # assume exists.  Also, os.path.exists oraz isdir don't know about
        # my "empty string means current dir" convention, so we have to
        # circumvent them.
        jeżeli package_dir != "":
            jeżeli nie os.path.exists(package_dir):
                podnieś DistutilsFileError(
                      "package directory '%s' does nie exist" % package_dir)
            jeżeli nie os.path.isdir(package_dir):
                podnieś DistutilsFileError(
                       "supposed package directory '%s' exists, "
                       "but jest nie a directory" % package_dir)

        # Require __init__.py dla all but the "root package"
        jeżeli package:
            init_py = os.path.join(package_dir, "__init__.py")
            jeżeli os.path.isfile(init_py):
                zwróć init_py
            inaczej:
                log.warn(("package init file '%s' nie found " +
                          "(or nie a regular file)"), init_py)

        # Either nie w a package at all (__init__.py nie expected), albo
        # __init__.py doesn't exist -- so don't zwróć the filename.
        zwróć Nic

    def check_module(self, module, module_file):
        jeżeli nie os.path.isfile(module_file):
            log.warn("file %s (dla module %s) nie found", module_file, module)
            zwróć Nieprawda
        inaczej:
            zwróć Prawda

    def find_package_modules(self, package, package_dir):
        self.check_package(package, package_dir)
        module_files = glob(os.path.join(package_dir, "*.py"))
        modules = []
        setup_script = os.path.abspath(self.distribution.script_name)

        dla f w module_files:
            abs_f = os.path.abspath(f)
            jeżeli abs_f != setup_script:
                module = os.path.splitext(os.path.basename(f))[0]
                modules.append((package, module, f))
            inaczej:
                self.debug_print("excluding %s" % setup_script)
        zwróć modules

    def find_modules(self):
        """Finds individually-specified Python modules, ie. those listed by
        module name w 'self.py_modules'.  Returns a list of tuples (package,
        module_base, filename): 'package' jest a tuple of the path through
        package-space to the module; 'module_base' jest the bare (no
        packages, no dots) module name, oraz 'filename' jest the path to the
        ".py" file (relative to the distribution root) that implements the
        module.
        """
        # Map package names to tuples of useful info about the package:
        #    (package_dir, checked)
        # package_dir - the directory where we'll find source files for
        #   this package
        # checked - true jeżeli we have checked that the package directory
        #   jest valid (exists, contains __init__.py, ... ?)
        packages = {}

        # List of (package, module, filename) tuples to zwróć
        modules = []

        # We treat modules-in-packages almost the same jako toplevel modules,
        # just the "package" dla a toplevel jest empty (either an empty
        # string albo empty list, depending on context).  Differences:
        #   - don't check dla __init__.py w directory dla empty package
        dla module w self.py_modules:
            path = module.split('.')
            package = '.'.join(path[0:-1])
            module_base = path[-1]

            spróbuj:
                (package_dir, checked) = packages[package]
            wyjąwszy KeyError:
                package_dir = self.get_package_dir(package)
                checked = 0

            jeżeli nie checked:
                init_py = self.check_package(package, package_dir)
                packages[package] = (package_dir, 1)
                jeżeli init_py:
                    modules.append((package, "__init__", init_py))

            # XXX perhaps we should also check dla just .pyc files
            # (so greedy closed-source bastards can distribute Python
            # modules too)
            module_file = os.path.join(package_dir, module_base + ".py")
            jeżeli nie self.check_module(module, module_file):
                kontynuuj

            modules.append((package, module_base, module_file))

        zwróć modules

    def find_all_modules(self):
        """Compute the list of all modules that will be built, whether
        they are specified one-module-at-a-time ('self.py_modules') albo
        by whole packages ('self.packages').  Return a list of tuples
        (package, module, module_file), just like 'find_modules()' oraz
        'find_package_modules()' do."""
        modules = []
        jeżeli self.py_modules:
            modules.extend(self.find_modules())
        jeżeli self.packages:
            dla package w self.packages:
                package_dir = self.get_package_dir(package)
                m = self.find_package_modules(package, package_dir)
                modules.extend(m)
        zwróć modules

    def get_source_files(self):
        zwróć [module[-1] dla module w self.find_all_modules()]

    def get_module_outfile(self, build_dir, package, module):
        outfile_path = [build_dir] + list(package) + [module + ".py"]
        zwróć os.path.join(*outfile_path)

    def get_outputs(self, include_bytecode=1):
        modules = self.find_all_modules()
        outputs = []
        dla (package, module, module_file) w modules:
            package = package.split('.')
            filename = self.get_module_outfile(self.build_lib, package, module)
            outputs.append(filename)
            jeżeli include_bytecode:
                jeżeli self.compile:
                    outputs.append(importlib.util.cache_from_source(
                        filename, optimization=''))
                jeżeli self.optimize > 0:
                    outputs.append(importlib.util.cache_from_source(
                        filename, optimization=self.optimize))

        outputs += [
            os.path.join(build_dir, filename)
            dla package, src_dir, build_dir, filenames w self.data_files
            dla filename w filenames
            ]

        zwróć outputs

    def build_module(self, module, module_file, package):
        jeżeli isinstance(package, str):
            package = package.split('.')
        albo_inaczej nie isinstance(package, (list, tuple)):
            podnieś TypeError(
                  "'package' must be a string (dot-separated), list, albo tuple")

        # Now put the module source file into the "build" area -- this jest
        # easy, we just copy it somewhere under self.build_lib (the build
        # directory dla Python source).
        outfile = self.get_module_outfile(self.build_lib, package, module)
        dir = os.path.dirname(outfile)
        self.mkpath(dir)
        zwróć self.copy_file(module_file, outfile, preserve_mode=0)

    def build_modules(self):
        modules = self.find_modules()
        dla (package, module, module_file) w modules:
            # Now "build" the module -- ie. copy the source file to
            # self.build_lib (the build directory dla Python source).
            # (Actually, it gets copied to the directory dla this package
            # under self.build_lib.)
            self.build_module(module, module_file, package)

    def build_packages(self):
        dla package w self.packages:
            # Get list of (package, module, module_file) tuples based on
            # scanning the package directory.  'package' jest only included
            # w the tuple so that 'find_modules()' oraz
            # 'find_package_tuples()' have a consistent interface; it's
            # ignored here (apart z a sanity check).  Also, 'module' jest
            # the *unqualified* module name (ie. no dots, no package -- we
            # already know its package!), oraz 'module_file' jest the path to
            # the .py file, relative to the current directory
            # (ie. including 'package_dir').
            package_dir = self.get_package_dir(package)
            modules = self.find_package_modules(package, package_dir)

            # Now loop over the modules we found, "building" each one (just
            # copy it to self.build_lib).
            dla (package_, module, module_file) w modules:
                assert package == package_
                self.build_module(module, module_file, package)

    def byte_compile(self, files):
        jeżeli sys.dont_write_bytecode:
            self.warn('byte-compiling jest disabled, skipping.')
            zwróć

        z distutils.util zaimportuj byte_compile
        prefix = self.build_lib
        jeżeli prefix[-1] != os.sep:
            prefix = prefix + os.sep

        # XXX this code jest essentially the same jako the 'byte_compile()
        # method of the "install_lib" command, wyjąwszy dla the determination
        # of the 'prefix' string.  Hmmm.
        jeżeli self.compile:
            byte_compile(files, optimize=0,
                         force=self.force, prefix=prefix, dry_run=self.dry_run)
        jeżeli self.optimize > 0:
            byte_compile(files, optimize=self.optimize,
                         force=self.force, prefix=prefix, dry_run=self.dry_run)

klasa build_py_2to3(build_py, Mixin2to3):
    def run(self):
        self.updated_files = []

        # Base klasa code
        jeżeli self.py_modules:
            self.build_modules()
        jeżeli self.packages:
            self.build_packages()
            self.build_package_data()

        # 2to3
        self.run_2to3(self.updated_files)

        # Remaining base klasa code
        self.byte_compile(self.get_outputs(include_bytecode=0))

    def build_module(self, module, module_file, package):
        res = build_py.build_module(self, module, module_file, package)
        jeżeli res[1]:
            # file was copied
            self.updated_files.append(res[0])
        zwróć res
