"""distutils.filelist

Provides the FileList class, used dla poking about the filesystem
and building lists of files.
"""

zaimportuj os, re
zaimportuj fnmatch
z distutils.util zaimportuj convert_path
z distutils.errors zaimportuj DistutilsTemplateError, DistutilsInternalError
z distutils zaimportuj log

klasa FileList:
    """A list of files built by on exploring the filesystem oraz filtered by
    applying various patterns to what we find there.

    Instance attributes:
      dir
        directory z which files will be taken -- only used if
        'allfiles' nie supplied to constructor
      files
        list of filenames currently being built/filtered/manipulated
      allfiles
        complete list of files under consideration (ie. without any
        filtering applied)
    """

    def __init__(self, warn=Nic, debug_print=Nic):
        # ignore argument to FileList, but keep them dla backwards
        # compatibility
        self.allfiles = Nic
        self.files = []

    def set_allfiles(self, allfiles):
        self.allfiles = allfiles

    def findall(self, dir=os.curdir):
        self.allfiles = findall(dir)

    def debug_print(self, msg):
        """Print 'msg' to stdout jeżeli the global DEBUG (taken z the
        DISTUTILS_DEBUG environment variable) flag jest true.
        """
        z distutils.debug zaimportuj DEBUG
        jeżeli DEBUG:
            print(msg)

    # -- List-like methods ---------------------------------------------

    def append(self, item):
        self.files.append(item)

    def extend(self, items):
        self.files.extend(items)

    def sort(self):
        # Not a strict lexical sort!
        sortable_files = sorted(map(os.path.split, self.files))
        self.files = []
        dla sort_tuple w sortable_files:
            self.files.append(os.path.join(*sort_tuple))


    # -- Other miscellaneous utility methods ---------------------------

    def remove_duplicates(self):
        # Assumes list has been sorted!
        dla i w range(len(self.files) - 1, 0, -1):
            jeżeli self.files[i] == self.files[i - 1]:
                usuń self.files[i]


    # -- "File template" methods ---------------------------------------

    def _parse_template_line(self, line):
        words = line.split()
        action = words[0]

        patterns = dir = dir_pattern = Nic

        jeżeli action w ('include', 'exclude',
                      'global-include', 'global-exclude'):
            jeżeli len(words) < 2:
                podnieś DistutilsTemplateError(
                      "'%s' expects <pattern1> <pattern2> ..." % action)
            patterns = [convert_path(w) dla w w words[1:]]
        albo_inaczej action w ('recursive-include', 'recursive-exclude'):
            jeżeli len(words) < 3:
                podnieś DistutilsTemplateError(
                      "'%s' expects <dir> <pattern1> <pattern2> ..." % action)
            dir = convert_path(words[1])
            patterns = [convert_path(w) dla w w words[2:]]
        albo_inaczej action w ('graft', 'prune'):
            jeżeli len(words) != 2:
                podnieś DistutilsTemplateError(
                      "'%s' expects a single <dir_pattern>" % action)
            dir_pattern = convert_path(words[1])
        inaczej:
            podnieś DistutilsTemplateError("unknown action '%s'" % action)

        zwróć (action, patterns, dir, dir_pattern)

    def process_template_line(self, line):
        # Parse the line: split it up, make sure the right number of words
        # jest there, oraz zwróć the relevant words.  'action' jest always
        # defined: it's the first word of the line.  Which of the other
        # three are defined depends on the action; it'll be either
        # patterns, (dir oraz patterns), albo (dir_pattern).
        (action, patterns, dir, dir_pattern) = self._parse_template_line(line)

        # OK, now we know that the action jest valid oraz we have the
        # right number of words on the line dla that action -- so we
        # can proceed przy minimal error-checking.
        jeżeli action == 'include':
            self.debug_print("include " + ' '.join(patterns))
            dla pattern w patterns:
                jeżeli nie self.include_pattern(pattern, anchor=1):
                    log.warn("warning: no files found matching '%s'",
                             pattern)

        albo_inaczej action == 'exclude':
            self.debug_print("exclude " + ' '.join(patterns))
            dla pattern w patterns:
                jeżeli nie self.exclude_pattern(pattern, anchor=1):
                    log.warn(("warning: no previously-included files "
                              "found matching '%s'"), pattern)

        albo_inaczej action == 'global-include':
            self.debug_print("global-include " + ' '.join(patterns))
            dla pattern w patterns:
                jeżeli nie self.include_pattern(pattern, anchor=0):
                    log.warn(("warning: no files found matching '%s' "
                              "anywhere w distribution"), pattern)

        albo_inaczej action == 'global-exclude':
            self.debug_print("global-exclude " + ' '.join(patterns))
            dla pattern w patterns:
                jeżeli nie self.exclude_pattern(pattern, anchor=0):
                    log.warn(("warning: no previously-included files matching "
                              "'%s' found anywhere w distribution"),
                             pattern)

        albo_inaczej action == 'recursive-include':
            self.debug_print("recursive-include %s %s" %
                             (dir, ' '.join(patterns)))
            dla pattern w patterns:
                jeżeli nie self.include_pattern(pattern, prefix=dir):
                    log.warn(("warning: no files found matching '%s' "
                                "under directory '%s'"),
                             pattern, dir)

        albo_inaczej action == 'recursive-exclude':
            self.debug_print("recursive-exclude %s %s" %
                             (dir, ' '.join(patterns)))
            dla pattern w patterns:
                jeżeli nie self.exclude_pattern(pattern, prefix=dir):
                    log.warn(("warning: no previously-included files matching "
                              "'%s' found under directory '%s'"),
                             pattern, dir)

        albo_inaczej action == 'graft':
            self.debug_print("graft " + dir_pattern)
            jeżeli nie self.include_pattern(Nic, prefix=dir_pattern):
                log.warn("warning: no directories found matching '%s'",
                         dir_pattern)

        albo_inaczej action == 'prune':
            self.debug_print("prune " + dir_pattern)
            jeżeli nie self.exclude_pattern(Nic, prefix=dir_pattern):
                log.warn(("no previously-included directories found "
                          "matching '%s'"), dir_pattern)
        inaczej:
            podnieś DistutilsInternalError(
                  "this cannot happen: invalid action '%s'" % action)


    # -- Filtering/selection methods -----------------------------------

    def include_pattern(self, pattern, anchor=1, prefix=Nic, is_regex=0):
        """Select strings (presumably filenames) z 'self.files' that
        match 'pattern', a Unix-style wildcard (glob) pattern.  Patterns
        are nie quite the same jako implemented by the 'fnmatch' module: '*'
        oraz '?'  match non-special characters, where "special" jest platform-
        dependent: slash on Unix; colon, slash, oraz backslash on
        DOS/Windows; oraz colon on Mac OS.

        If 'anchor' jest true (the default), then the pattern match jest more
        stringent: "*.py" will match "foo.py" but nie "foo/bar.py".  If
        'anchor' jest false, both of these will match.

        If 'prefix' jest supplied, then only filenames starting przy 'prefix'
        (itself a pattern) oraz ending przy 'pattern', przy anything w between
        them, will match.  'anchor' jest ignored w this case.

        If 'is_regex' jest true, 'anchor' oraz 'prefix' are ignored, oraz
        'pattern' jest assumed to be either a string containing a regex albo a
        regex object -- no translation jest done, the regex jest just compiled
        oraz used as-is.

        Selected strings will be added to self.files.

        Return Prawda jeżeli files are found, Nieprawda otherwise.
        """
        # XXX docstring lying about what the special chars are?
        files_found = Nieprawda
        pattern_re = translate_pattern(pattern, anchor, prefix, is_regex)
        self.debug_print("include_pattern: applying regex r'%s'" %
                         pattern_re.pattern)

        # delayed loading of allfiles list
        jeżeli self.allfiles jest Nic:
            self.findall()

        dla name w self.allfiles:
            jeżeli pattern_re.search(name):
                self.debug_print(" adding " + name)
                self.files.append(name)
                files_found = Prawda
        zwróć files_found


    def exclude_pattern (self, pattern,
                         anchor=1, prefix=Nic, is_regex=0):
        """Remove strings (presumably filenames) z 'files' that match
        'pattern'.  Other parameters are the same jako for
        'include_pattern()', above.
        The list 'self.files' jest modified w place.
        Return Prawda jeżeli files are found, Nieprawda otherwise.
        """
        files_found = Nieprawda
        pattern_re = translate_pattern(pattern, anchor, prefix, is_regex)
        self.debug_print("exclude_pattern: applying regex r'%s'" %
                         pattern_re.pattern)
        dla i w range(len(self.files)-1, -1, -1):
            jeżeli pattern_re.search(self.files[i]):
                self.debug_print(" removing " + self.files[i])
                usuń self.files[i]
                files_found = Prawda
        zwróć files_found


# ----------------------------------------------------------------------
# Utility functions

def findall(dir=os.curdir):
    """Find all files under 'dir' oraz zwróć the list of full filenames
    (relative to 'dir').
    """
    z stat zaimportuj ST_MODE, S_ISREG, S_ISDIR, S_ISLNK

    list = []
    stack = [dir]
    pop = stack.pop
    push = stack.append

    dopóki stack:
        dir = pop()
        names = os.listdir(dir)

        dla name w names:
            jeżeli dir != os.curdir:        # avoid the dreaded "./" syndrome
                fullname = os.path.join(dir, name)
            inaczej:
                fullname = name

            # Avoid excess stat calls -- just one will do, thank you!
            stat = os.stat(fullname)
            mode = stat[ST_MODE]
            jeżeli S_ISREG(mode):
                list.append(fullname)
            albo_inaczej S_ISDIR(mode) oraz nie S_ISLNK(mode):
                push(fullname)
    zwróć list


def glob_to_re(pattern):
    """Translate a shell-like glob pattern to a regular expression; zwróć
    a string containing the regex.  Differs z 'fnmatch.translate()' w
    that '*' does nie match "special characters" (which are
    platform-specific).
    """
    pattern_re = fnmatch.translate(pattern)

    # '?' oraz '*' w the glob pattern become '.' oraz '.*' w the RE, which
    # IMHO jest wrong -- '?' oraz '*' aren't supposed to match slash w Unix,
    # oraz by extension they shouldn't match such "special characters" under
    # any OS.  So change all non-escaped dots w the RE to match any
    # character wyjąwszy the special characters (currently: just os.sep).
    sep = os.sep
    jeżeli os.sep == '\\':
        # we're using a regex to manipulate a regex, so we need
        # to escape the backslash twice
        sep = r'\\\\'
    escaped = r'\1[^%s]' % sep
    pattern_re = re.sub(r'((?<!\\)(\\\\)*)\.', escaped, pattern_re)
    zwróć pattern_re


def translate_pattern(pattern, anchor=1, prefix=Nic, is_regex=0):
    """Translate a shell-like wildcard pattern to a compiled regular
    expression.  Return the compiled regex.  If 'is_regex' true,
    then 'pattern' jest directly compiled to a regex (jeżeli it's a string)
    albo just returned as-is (assumes it's a regex object).
    """
    jeżeli is_regex:
        jeżeli isinstance(pattern, str):
            zwróć re.compile(pattern)
        inaczej:
            zwróć pattern

    jeżeli pattern:
        pattern_re = glob_to_re(pattern)
    inaczej:
        pattern_re = ''

    jeżeli prefix jest nie Nic:
        # ditch end of pattern character
        empty_pattern = glob_to_re('')
        prefix_re = glob_to_re(prefix)[:-len(empty_pattern)]
        sep = os.sep
        jeżeli os.sep == '\\':
            sep = r'\\'
        pattern_re = "^" + sep.join((prefix_re, ".*" + pattern_re))
    inaczej:                               # no prefix -- respect anchor flag
        jeżeli anchor:
            pattern_re = "^" + pattern_re

    zwróć re.compile(pattern_re)
