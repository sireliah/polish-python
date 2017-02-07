"""
Main program dla 2to3.
"""

z __future__ zaimportuj with_statement, print_function

zaimportuj sys
zaimportuj os
zaimportuj difflib
zaimportuj logging
zaimportuj shutil
zaimportuj optparse

z . zaimportuj refactor


def diff_texts(a, b, filename):
    """Return a unified diff of two strings."""
    a = a.splitlines()
    b = b.splitlines()
    zwróć difflib.unified_diff(a, b, filename, filename,
                                "(original)", "(refactored)",
                                lineterm="")


klasa StdoutRefactoringTool(refactor.MultiprocessRefactoringTool):
    """
    A refactoring tool that can avoid overwriting its input files.
    Prints output to stdout.

    Output files can optionally be written to a different directory oraz albo
    have an extra file suffix appended to their name dla use w situations
    where you do nie want to replace the input files.
    """

    def __init__(self, fixers, options, explicit, nobackups, show_diffs,
                 input_base_dir='', output_dir='', append_suffix=''):
        """
        Args:
            fixers: A list of fixers to import.
            options: A dict przy RefactoringTool configuration.
            explicit: A list of fixers to run even jeżeli they are explicit.
            nobackups: If true no backup '.bak' files will be created dla those
                files that are being refactored.
            show_diffs: Should diffs of the refactoring be printed to stdout?
            input_base_dir: The base directory dla all input files.  This class
                will strip this path prefix off of filenames before substituting
                it przy output_dir.  Only meaningful jeżeli output_dir jest supplied.
                All files processed by refactor() must start przy this path.
            output_dir: If supplied, all converted files will be written into
                this directory tree instead of input_base_dir.
            append_suffix: If supplied, all files output by this tool will have
                this appended to their filename.  Useful dla changing .py to
                .py3 dla example by dalejing append_suffix='3'.
        """
        self.nobackups = nobackups
        self.show_diffs = show_diffs
        jeżeli input_base_dir oraz nie input_base_dir.endswith(os.sep):
            input_base_dir += os.sep
        self._input_base_dir = input_base_dir
        self._output_dir = output_dir
        self._append_suffix = append_suffix
        super(StdoutRefactoringTool, self).__init__(fixers, options, explicit)

    def log_error(self, msg, *args, **kwargs):
        self.errors.append((msg, args, kwargs))
        self.logger.error(msg, *args, **kwargs)

    def write_file(self, new_text, filename, old_text, encoding):
        orig_filename = filename
        jeżeli self._output_dir:
            jeżeli filename.startswith(self._input_base_dir):
                filename = os.path.join(self._output_dir,
                                        filename[len(self._input_base_dir):])
            inaczej:
                podnieś ValueError('filename %s does nie start przy the '
                                 'input_base_dir %s' % (
                                         filename, self._input_base_dir))
        jeżeli self._append_suffix:
            filename += self._append_suffix
        jeżeli orig_filename != filename:
            output_dir = os.path.dirname(filename)
            jeżeli nie os.path.isdir(output_dir):
                os.makedirs(output_dir)
            self.log_message('Writing converted %s to %s.', orig_filename,
                             filename)
        jeżeli nie self.nobackups:
            # Make backup
            backup = filename + ".bak"
            jeżeli os.path.lexists(backup):
                spróbuj:
                    os.remove(backup)
                wyjąwszy OSError jako err:
                    self.log_message("Can't remove backup %s", backup)
            spróbuj:
                os.rename(filename, backup)
            wyjąwszy OSError jako err:
                self.log_message("Can't rename %s to %s", filename, backup)
        # Actually write the new file
        write = super(StdoutRefactoringTool, self).write_file
        write(new_text, filename, old_text, encoding)
        jeżeli nie self.nobackups:
            shutil.copymode(backup, filename)
        jeżeli orig_filename != filename:
            # Preserve the file mode w the new output directory.
            shutil.copymode(orig_filename, filename)

    def print_output(self, old, new, filename, equal):
        jeżeli equal:
            self.log_message("No changes to %s", filename)
        inaczej:
            self.log_message("Refactored %s", filename)
            jeżeli self.show_diffs:
                diff_lines = diff_texts(old, new, filename)
                spróbuj:
                    jeżeli self.output_lock jest nie Nic:
                        przy self.output_lock:
                            dla line w diff_lines:
                                print(line)
                            sys.stdout.flush()
                    inaczej:
                        dla line w diff_lines:
                            print(line)
                wyjąwszy UnicodeEncodeError:
                    warn("couldn't encode %s's diff dla your terminal" %
                         (filename,))
                    zwróć

def warn(msg):
    print("WARNING: %s" % (msg,), file=sys.stderr)


def main(fixer_pkg, args=Nic):
    """Main program.

    Args:
        fixer_pkg: the name of a package where the fixers are located.
        args: optional; a list of command line arguments. If omitted,
              sys.argv[1:] jest used.

    Returns a suggested exit status (0, 1, 2).
    """
    # Set up option parser
    parser = optparse.OptionParser(usage="2to3 [options] file|dir ...")
    parser.add_option("-d", "--doctests_only", action="store_true",
                      help="Fix up doctests only")
    parser.add_option("-f", "--fix", action="append", default=[],
                      help="Each FIX specifies a transformation; default: all")
    parser.add_option("-j", "--processes", action="store", default=1,
                      type="int", help="Run 2to3 concurrently")
    parser.add_option("-x", "--nofix", action="append", default=[],
                      help="Prevent a transformation z being run")
    parser.add_option("-l", "--list-fixes", action="store_true",
                      help="List available transformations")
    parser.add_option("-p", "--print-function", action="store_true",
                      help="Modify the grammar so that print() jest a function")
    parser.add_option("-v", "--verbose", action="store_true",
                      help="More verbose logging")
    parser.add_option("--no-diffs", action="store_true",
                      help="Don't show diffs of the refactoring")
    parser.add_option("-w", "--write", action="store_true",
                      help="Write back modified files")
    parser.add_option("-n", "--nobackups", action="store_true", default=Nieprawda,
                      help="Don't write backups dla modified files")
    parser.add_option("-o", "--output-dir", action="store", type="str",
                      default="", help="Put output files w this directory "
                      "instead of overwriting the input files.  Requires -n.")
    parser.add_option("-W", "--write-unchanged-files", action="store_true",
                      help="Also write files even jeżeli no changes were required"
                      " (useful przy --output-dir); implies -w.")
    parser.add_option("--add-suffix", action="store", type="str", default="",
                      help="Append this string to all output filenames."
                      " Requires -n jeżeli non-empty.  "
                      "ex: --add-suffix='3' will generate .py3 files.")

    # Parse command line arguments
    refactor_stdin = Nieprawda
    flags = {}
    options, args = parser.parse_args(args)
    jeżeli options.write_unchanged_files:
        flags["write_unchanged_files"] = Prawda
        jeżeli nie options.write:
            warn("--write-unchanged-files/-W implies -w.")
        options.write = Prawda
    # If we allowed these, the original files would be renamed to backup names
    # but nie replaced.
    jeżeli options.output_dir oraz nie options.nobackups:
        parser.error("Can't use --output-dir/-o without -n.")
    jeżeli options.add_suffix oraz nie options.nobackups:
        parser.error("Can't use --add-suffix without -n.")

    jeżeli nie options.write oraz options.no_diffs:
        warn("not writing files oraz nie printing diffs; that's nie very useful")
    jeżeli nie options.write oraz options.nobackups:
        parser.error("Can't use -n without -w")
    jeżeli options.list_fixes:
        print("Available transformations dla the -f/--fix option:")
        dla fixname w refactor.get_all_fix_names(fixer_pkg):
            print(fixname)
        jeżeli nie args:
            zwróć 0
    jeżeli nie args:
        print("At least one file albo directory argument required.", file=sys.stderr)
        print("Use --help to show usage.", file=sys.stderr)
        zwróć 2
    jeżeli "-" w args:
        refactor_stdin = Prawda
        jeżeli options.write:
            print("Can't write to stdin.", file=sys.stderr)
            zwróć 2
    jeżeli options.print_function:
        flags["print_function"] = Prawda

    # Set up logging handler
    level = logging.DEBUG jeżeli options.verbose inaczej logging.INFO
    logging.basicConfig(format='%(name)s: %(message)s', level=level)
    logger = logging.getLogger('lib2to3.main')

    # Initialize the refactoring tool
    avail_fixes = set(refactor.get_fixers_from_package(fixer_pkg))
    unwanted_fixes = set(fixer_pkg + ".fix_" + fix dla fix w options.nofix)
    explicit = set()
    jeżeli options.fix:
        all_present = Nieprawda
        dla fix w options.fix:
            jeżeli fix == "all":
                all_present = Prawda
            inaczej:
                explicit.add(fixer_pkg + ".fix_" + fix)
        requested = avail_fixes.union(explicit) jeżeli all_present inaczej explicit
    inaczej:
        requested = avail_fixes.union(explicit)
    fixer_names = requested.difference(unwanted_fixes)
    input_base_dir = os.path.commonprefix(args)
    jeżeli (input_base_dir oraz nie input_base_dir.endswith(os.sep)
        oraz nie os.path.isdir(input_base_dir)):
        # One albo more similar names were dalejed, their directory jest the base.
        # os.path.commonprefix() jest ignorant of path elements, this corrects
        # dla that weird API.
        input_base_dir = os.path.dirname(input_base_dir)
    jeżeli options.output_dir:
        input_base_dir = input_base_dir.rstrip(os.sep)
        logger.info('Output w %r will mirror the input directory %r layout.',
                    options.output_dir, input_base_dir)
    rt = StdoutRefactoringTool(
            sorted(fixer_names), flags, sorted(explicit),
            options.nobackups, nie options.no_diffs,
            input_base_dir=input_base_dir,
            output_dir=options.output_dir,
            append_suffix=options.add_suffix)

    # Refactor all files oraz directories dalejed jako arguments
    jeżeli nie rt.errors:
        jeżeli refactor_stdin:
            rt.refactor_stdin()
        inaczej:
            spróbuj:
                rt.refactor(args, options.write, options.doctests_only,
                            options.processes)
            wyjąwszy refactor.MultiprocessingUnsupported:
                assert options.processes > 1
                print("Sorry, -j isn't supported on this platform.",
                      file=sys.stderr)
                zwróć 1
        rt.summarize()

    # Return error status (0 jeżeli rt.errors jest zero)
    zwróć int(bool(rt.errors))
