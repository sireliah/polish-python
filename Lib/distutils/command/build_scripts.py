"""distutils.command.build_scripts

Implements the Distutils 'build_scripts' command."""

zaimportuj os, re
z stat zaimportuj ST_MODE
z distutils zaimportuj sysconfig
z distutils.core zaimportuj Command
z distutils.dep_util zaimportuj newer
z distutils.util zaimportuj convert_path, Mixin2to3
z distutils zaimportuj log
zaimportuj tokenize

# check jeżeli Python jest called on the first line przy this expression
first_line_re = re.compile(b'^#!.*python[0-9.]*([ \t].*)?$')

klasa build_scripts(Command):

    description = "\"build\" scripts (copy oraz fixup #! line)"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" (copy) to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ('executable=', 'e', "specify final destination interpreter path"),
        ]

    boolean_options = ['force']


    def initialize_options(self):
        self.build_dir = Nic
        self.scripts = Nic
        self.force = Nic
        self.executable = Nic
        self.outfiles = Nic

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_scripts', 'build_dir'),
                                   ('force', 'force'),
                                   ('executable', 'executable'))
        self.scripts = self.distribution.scripts

    def get_source_files(self):
        zwróć self.scripts

    def run(self):
        jeżeli nie self.scripts:
            zwróć
        self.copy_scripts()


    def copy_scripts(self):
        """Copy each script listed w 'self.scripts'; jeżeli it's marked jako a
        Python script w the Unix way (first line matches 'first_line_re',
        ie. starts przy "\#!" oraz contains "python"), then adjust the first
        line to refer to the current Python interpreter jako we copy.
        """
        self.mkpath(self.build_dir)
        outfiles = []
        updated_files = []
        dla script w self.scripts:
            adjust = Nieprawda
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)

            jeżeli nie self.force oraz nie newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                kontynuuj

            # Always open the file, but ignore failures w dry-run mode --
            # that way, we'll get accurate feedback jeżeli we can read the
            # script.
            spróbuj:
                f = open(script, "rb")
            wyjąwszy OSError:
                jeżeli nie self.dry_run:
                    podnieś
                f = Nic
            inaczej:
                encoding, lines = tokenize.detect_encoding(f.readline)
                f.seek(0)
                first_line = f.readline()
                jeżeli nie first_line:
                    self.warn("%s jest an empty file (skipping)" % script)
                    kontynuuj

                match = first_line_re.match(first_line)
                jeżeli match:
                    adjust = Prawda
                    post_interp = match.group(1) albo b''

            jeżeli adjust:
                log.info("copying oraz adjusting %s -> %s", script,
                         self.build_dir)
                updated_files.append(outfile)
                jeżeli nie self.dry_run:
                    jeżeli nie sysconfig.python_build:
                        executable = self.executable
                    inaczej:
                        executable = os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                           "python%s%s" % (sysconfig.get_config_var("VERSION"),
                                           sysconfig.get_config_var("EXE")))
                    executable = os.fsencode(executable)
                    shebang = b"#!" + executable + post_interp + b"\n"
                    # Python parser starts to read a script using UTF-8 until
                    # it gets a #coding:xxx cookie. The shebang has to be the
                    # first line of a file, the #coding:xxx cookie cannot be
                    # written before. So the shebang has to be decodable from
                    # UTF-8.
                    spróbuj:
                        shebang.decode('utf-8')
                    wyjąwszy UnicodeDecodeError:
                        podnieś ValueError(
                            "The shebang ({!r}) jest nie decodable "
                            "z utf-8".format(shebang))
                    # If the script jest encoded to a custom encoding (use a
                    # #coding:xxx cookie), the shebang has to be decodable from
                    # the script encoding too.
                    spróbuj:
                        shebang.decode(encoding)
                    wyjąwszy UnicodeDecodeError:
                        podnieś ValueError(
                            "The shebang ({!r}) jest nie decodable "
                            "z the script encoding ({})"
                            .format(shebang, encoding))
                    przy open(outfile, "wb") jako outf:
                        outf.write(shebang)
                        outf.writelines(f.readlines())
                jeżeli f:
                    f.close()
            inaczej:
                jeżeli f:
                    f.close()
                updated_files.append(outfile)
                self.copy_file(script, outfile)

        jeżeli os.name == 'posix':
            dla file w outfiles:
                jeżeli self.dry_run:
                    log.info("changing mode of %s", file)
                inaczej:
                    oldmode = os.stat(file)[ST_MODE] & 0o7777
                    newmode = (oldmode | 0o555) & 0o7777
                    jeżeli newmode != oldmode:
                        log.info("changing mode of %s z %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)
        # XXX should we modify self.outfiles?
        zwróć outfiles, updated_files

klasa build_scripts_2to3(build_scripts, Mixin2to3):

    def copy_scripts(self):
        outfiles, updated_files = build_scripts.copy_scripts(self)
        jeżeli nie self.dry_run:
            self.run_2to3(updated_files)
        zwróć outfiles, updated_files
