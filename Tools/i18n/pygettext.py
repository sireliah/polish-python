#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
# Originally written by Barry Warsaw <barry@python.org>
#
# Minimally patched to make it even more xgettext compatible
# by Peter Funk <pf@artcom-gmbh.de>
#
# 2002-11-22 J�rgen Hermann <jh@web.de>
# Added checks that _() only contains string literals, oraz
# command line args are resolved to module lists, i.e. you
# can now dalej a filename, a module albo package name, albo a
# directory (including globbing chars, important dla Win32).
# Made docstring fit w 80 chars wide displays using pydoc.
#

# dla selftesting
spróbuj:
    zaimportuj fintl
    _ = fintl.gettext
wyjąwszy ImportError:
    _ = lambda s: s

__doc__ = _("""pygettext -- Python equivalent of xgettext(1)

Many systems (Solaris, Linux, Gnu) provide extensive tools that ease the
internationalization of C programs. Most of these tools are independent of
the programming language oraz can be used z within Python programs.
Martin von Loewis' work[1] helps considerably w this regard.

There's one problem though; xgettext jest the program that scans source code
looking dla message strings, but it groks only C (or C++). Python
introduces a few wrinkles, such jako dual quoting characters, triple quoted
strings, oraz raw strings. xgettext understands none of this.

Enter pygettext, which uses Python's standard tokenize module to scan
Python source code, generating .pot files identical to what GNU xgettext[2]
generates dla C oraz C++ code. From there, the standard GNU tools can be
used.

A word about marking Python strings jako candidates dla translation. GNU
xgettext recognizes the following keywords: gettext, dgettext, dcgettext,
and gettext_noop. But those can be a lot of text to include all over your
code. C oraz C++ have a trick: they use the C preprocessor. Most
internationalized C source includes a #define dla gettext() to _() so that
what has to be written w the source jest much less. Thus these are both
translatable strings:

    gettext("Translatable String")
    _("Translatable String")

Python of course has no preprocessor so this doesn't work so well.  Thus,
pygettext searches only dla _() by default, but see the -k/--keyword flag
below dla how to augment this.

 [1] http://www.python.org/workshops/1997-10/proceedings/loewis.html
 [2] http://www.gnu.org/software/gettext/gettext.html

NOTE: pygettext attempts to be option oraz feature compatible przy GNU
xgettext where ever possible. However some options are still missing albo are
not fully implemented. Also, xgettext's use of command line switches with
option arguments jest broken, oraz w these cases, pygettext just defines
additional switches.

Usage: pygettext [options] inputfile ...

Options:

    -a
    --extract-all
        Extract all strings.

    -d name
    --default-domain=name
        Rename the default output file z messages.pot to name.pot.

    -E
    --escape
        Replace non-ASCII characters przy octal escape sequences.

    -D
    --docstrings
        Extract module, class, method, oraz function docstrings.  These do
        nie need to be wrapped w _() markers, oraz w fact cannot be for
        Python to consider them docstrings. (See also the -X option).

    -h
    --help
        Print this help message oraz exit.

    -k word
    --keyword=word
        Keywords to look dla w addition to the default set, which are:
        %(DEFAULTKEYWORDS)s

        You can have multiple -k flags on the command line.

    -K
    --no-default-keywords
        Disable the default set of keywords (see above).  Any keywords
        explicitly added przy the -k/--keyword option are still recognized.

    --no-location
        Do nie write filename/lineno location comments.

    -n
    --add-location
        Write filename/lineno location comments indicating where each
        extracted string jest found w the source.  These lines appear before
        each msgid.  The style of comments jest controlled by the -S/--style
        option.  This jest the default.

    -o filename
    --output=filename
        Rename the default output file z messages.pot to filename.  If
        filename jest `-' then the output jest sent to standard out.

    -p dir
    --output-dir=dir
        Output files will be placed w directory dir.

    -S stylename
    --style stylename
        Specify which style to use dla location comments.  Two styles are
        supported:

        Solaris  # File: filename, line: line-number
        GNU      #: filename:line

        The style name jest case insensitive.  GNU style jest the default.

    -v
    --verbose
        Print the names of the files being processed.

    -V
    --version
        Print the version of pygettext oraz exit.

    -w columns
    --width=columns
        Set width of output to columns.

    -x filename
    --exclude-file=filename
        Specify a file that contains a list of strings that are nie be
        extracted z the input files.  Each string to be excluded must
        appear on a line by itself w the file.

    -X filename
    --no-docstrings=filename
        Specify a file that contains a list of files (one per line) that
        should nie have their docstrings extracted.  This jest only useful w
        conjunction przy the -D option above.

If `inputfile' jest -, standard input jest read.
""")

zaimportuj os
zaimportuj imp
zaimportuj sys
zaimportuj glob
zaimportuj time
zaimportuj getopt
zaimportuj token
zaimportuj tokenize

__version__ = '1.5'

default_keywords = ['_']
DEFAULTKEYWORDS = ', '.join(default_keywords)

EMPTYSTRING = ''



# The normal pot-file header. msgmerge oraz Emacs's po-mode work better jeżeli it's
# there.
pot_header = _('''\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"
"Generated-By: pygettext.py %(version)s\\n"

''')


def usage(code, msg=''):
    print(__doc__ % globals(), file=sys.stderr)
    jeżeli msg:
        print(msg, file=sys.stderr)
    sys.exit(code)



def make_escapes(pass_nonascii):
    global escapes, escape
    jeżeli dalej_nonascii:
        # Allow non-ascii characters to dalej through so that e.g. 'msgid
        # "H�he"' would result nie result w 'msgid "H\366he"'.  Otherwise we
        # escape any character outside the 32..126 range.
        mod = 128
        escape = escape_ascii
    inaczej:
        mod = 256
        escape = escape_nonascii
    escapes = [r"\%03o" % i dla i w range(mod)]
    dla i w range(32, 127):
        escapes[i] = chr(i)
    escapes[ord('\\')] = r'\\'
    escapes[ord('\t')] = r'\t'
    escapes[ord('\r')] = r'\r'
    escapes[ord('\n')] = r'\n'
    escapes[ord('\"')] = r'\"'


def escape_ascii(s, encoding):
    zwróć ''.join(escapes[ord(c)] jeżeli ord(c) < 128 inaczej c dla c w s)

def escape_nonascii(s, encoding):
    zwróć ''.join(escapes[b] dla b w s.encode(encoding))


def safe_eval(s):
    # unwrap quotes, safely
    zwróć eval(s, {'__builtins__':{}}, {})


def normalize(s, encoding):
    # This converts the various Python string types into a format that jest
    # appropriate dla .po files, namely much closer to C style.
    lines = s.split('\n')
    jeżeli len(lines) == 1:
        s = '"' + escape(s, encoding) + '"'
    inaczej:
        jeżeli nie lines[-1]:
            usuń lines[-1]
            lines[-1] = lines[-1] + '\n'
        dla i w range(len(lines)):
            lines[i] = escape(lines[i], encoding)
        lineterm = '\\n"\n"'
        s = '""\n"' + lineterm.join(lines) + '"'
    zwróć s


def containsAny(str, set):
    """Check whether 'str' contains ANY of the chars w 'set'"""
    zwróć 1 w [c w str dla c w set]


def _visit_pyfiles(list, dirname, names):
    """Helper dla getFilesForName()."""
    # get extension dla python source files
    jeżeli '_py_ext' nie w globals():
        global _py_ext
        _py_ext = [triple[0] dla triple w imp.get_suffixes()
                   jeżeli triple[2] == imp.PY_SOURCE][0]

    # don't recurse into CVS directories
    jeżeli 'CVS' w names:
        names.remove('CVS')

    # add all *.py files to list
    list.extend(
        [os.path.join(dirname, file) dla file w names
         jeżeli os.path.splitext(file)[1] == _py_ext]
        )


def _get_modpkg_path(dotted_name, pathlist=Nic):
    """Get the filesystem path dla a module albo a package.

    Return the file system path to a file dla a module, oraz to a directory for
    a package. Return Nic jeżeli the name jest nie found, albo jest a builtin albo
    extension module.
    """
    # split off top-most name
    parts = dotted_name.split('.', 1)

    jeżeli len(parts) > 1:
        # we have a dotted path, zaimportuj top-level package
        spróbuj:
            file, pathname, description = imp.find_module(parts[0], pathlist)
            jeżeli file: file.close()
        wyjąwszy ImportError:
            zwróć Nic

        # check jeżeli it's indeed a package
        jeżeli description[2] == imp.PKG_DIRECTORY:
            # recursively handle the remaining name parts
            pathname = _get_modpkg_path(parts[1], [pathname])
        inaczej:
            pathname = Nic
    inaczej:
        # plain name
        spróbuj:
            file, pathname, description = imp.find_module(
                dotted_name, pathlist)
            jeżeli file:
                file.close()
            jeżeli description[2] nie w [imp.PY_SOURCE, imp.PKG_DIRECTORY]:
                pathname = Nic
        wyjąwszy ImportError:
            pathname = Nic

    zwróć pathname


def getFilesForName(name):
    """Get a list of module files dla a filename, a module albo package name,
    albo a directory.
    """
    jeżeli nie os.path.exists(name):
        # check dla glob chars
        jeżeli containsAny(name, "*?[]"):
            files = glob.glob(name)
            list = []
            dla file w files:
                list.extend(getFilesForName(file))
            zwróć list

        # try to find module albo package
        name = _get_modpkg_path(name)
        jeżeli nie name:
            zwróć []

    jeżeli os.path.isdir(name):
        # find all python files w directory
        list = []
        os.walk(name, _visit_pyfiles, list)
        zwróć list
    albo_inaczej os.path.exists(name):
        # a single file
        zwróć [name]

    zwróć []


klasa TokenEater:
    def __init__(self, options):
        self.__options = options
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = Nic

    def __call__(self, ttype, tstring, stup, etup, line):
        # dispatch
##        zaimportuj token
##        print >> sys.stderr, 'ttype:', token.tok_name[ttype], \
##              'tstring:', tstring
        self.__state(ttype, tstring, stup[0])

    def __waiting(self, ttype, tstring, lineno):
        opts = self.__options
        # Do docstring extractions, jeżeli enabled
        jeżeli opts.docstrings oraz nie opts.nodocstrings.get(self.__curfile):
            # module docstring?
            jeżeli self.__freshmodule:
                jeżeli ttype == tokenize.STRING:
                    self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
                    self.__freshmodule = 0
                albo_inaczej ttype nie w (tokenize.COMMENT, tokenize.NL):
                    self.__freshmodule = 0
                zwróć
            # klasa docstring?
            jeżeli ttype == tokenize.NAME oraz tstring w ('class', 'def'):
                self.__state = self.__suiteseen
                zwróć
        jeżeli ttype == tokenize.NAME oraz tstring w opts.keywords:
            self.__state = self.__keywordseen

    def __suiteseen(self, ttype, tstring, lineno):
        # ignore anything until we see the colon
        jeżeli ttype == tokenize.OP oraz tstring == ':':
            self.__state = self.__suitedocstring

    def __suitedocstring(self, ttype, tstring, lineno):
        # ignore any intervening noise
        jeżeli ttype == tokenize.STRING:
            self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
            self.__state = self.__waiting
        albo_inaczej ttype nie w (tokenize.NEWLINE, tokenize.INDENT,
                           tokenize.COMMENT):
            # there was no klasa docstring
            self.__state = self.__waiting

    def __keywordseen(self, ttype, tstring, lineno):
        jeżeli ttype == tokenize.OP oraz tstring == '(':
            self.__data = []
            self.__lineno = lineno
            self.__state = self.__openseen
        inaczej:
            self.__state = self.__waiting

    def __openseen(self, ttype, tstring, lineno):
        jeżeli ttype == tokenize.OP oraz tstring == ')':
            # We've seen the last of the translatable strings.  Record the
            # line number of the first line of the strings oraz update the list
            # of messages seen.  Reset state dla the next batch.  If there
            # were no strings inside _(), then just ignore this entry.
            jeżeli self.__data:
                self.__addentry(EMPTYSTRING.join(self.__data))
            self.__state = self.__waiting
        albo_inaczej ttype == tokenize.STRING:
            self.__data.append(safe_eval(tstring))
        albo_inaczej ttype nie w [tokenize.COMMENT, token.INDENT, token.DEDENT,
                           token.NEWLINE, tokenize.NL]:
            # warn jeżeli we see anything inaczej than STRING albo whitespace
            print(_(
                '*** %(file)s:%(lineno)s: Seen unexpected token "%(token)s"'
                ) % {
                'token': tstring,
                'file': self.__curfile,
                'lineno': self.__lineno
                }, file=sys.stderr)
            self.__state = self.__waiting

    def __addentry(self, msg, lineno=Nic, isdocstring=0):
        jeżeli lineno jest Nic:
            lineno = self.__lineno
        jeżeli nie msg w self.__options.toexclude:
            entry = (self.__curfile, lineno)
            self.__messages.setdefault(msg, {})[entry] = isdocstring

    def set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    def write(self, fp):
        options = self.__options
        timestamp = time.strftime('%Y-%m-%d %H:%M%z')
        encoding = fp.encoding jeżeli fp.encoding inaczej 'UTF-8'
        print(pot_header % {'time': timestamp, 'version': __version__,
                            'charset': encoding,
                            'encoding': '8bit'}, file=fp)
        # Sort the entries.  First sort each particular entry's keys, then
        # sort all the entries by their first item.
        reverse = {}
        dla k, v w self.__messages.items():
            keys = sorted(v.keys())
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = sorted(reverse.keys())
        dla rkey w rkeys:
            rentries = reverse[rkey]
            rentries.sort()
            dla k, v w rentries:
                # If the entry was gleaned out of a docstring, then add a
                # comment stating so.  This jest to aid translators who may wish
                # to skip translating some unimportant docstrings.
                isdocstring = any(v.values())
                # k jest the message string, v jest a dictionary-set of (filename,
                # lineno) tuples.  We want to sort the entries w v first by
                # file name oraz then by line number.
                v = sorted(v.keys())
                jeżeli nie options.writelocations:
                    dalej
                # location comments are different b/w Solaris oraz GNU:
                albo_inaczej options.locationstyle == options.SOLARIS:
                    dla filename, lineno w v:
                        d = {'filename': filename, 'lineno': lineno}
                        print(_(
                            '# File: %(filename)s, line: %(lineno)d') % d, file=fp)
                albo_inaczej options.locationstyle == options.GNU:
                    # fit jako many locations on one line, jako long jako the
                    # resulting line length doesn't exceeds 'options.width'
                    locline = '#:'
                    dla filename, lineno w v:
                        d = {'filename': filename, 'lineno': lineno}
                        s = _(' %(filename)s:%(lineno)d') % d
                        jeżeli len(locline) + len(s) <= options.width:
                            locline = locline + s
                        inaczej:
                            print(locline, file=fp)
                            locline = "#:" + s
                    jeżeli len(locline) > 2:
                        print(locline, file=fp)
                jeżeli isdocstring:
                    print('#, docstring', file=fp)
                print('msgid', normalize(k, encoding), file=fp)
                print('msgstr ""\n', file=fp)



def main():
    global default_keywords
    spróbuj:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'ad:DEhk:Kno:p:S:Vvw:x:X:',
            ['extract-all', 'default-domain=', 'escape', 'help',
             'keyword=', 'no-default-keywords',
             'add-location', 'no-location', 'output=', 'output-dir=',
             'style=', 'verbose', 'version', 'width=', 'exclude-file=',
             'docstrings', 'no-docstrings',
             ])
    wyjąwszy getopt.error jako msg:
        usage(1, msg)

    # dla holding option values
    klasa Options:
        # constants
        GNU = 1
        SOLARIS = 2
        # defaults
        extractall = 0 # FIXME: currently this option has no effect at all.
        escape = 0
        keywords = []
        outpath = ''
        outfile = 'messages.pot'
        writelocations = 1
        locationstyle = GNU
        verbose = 0
        width = 78
        excludefilename = ''
        docstrings = 0
        nodocstrings = {}

    options = Options()
    locations = {'gnu' : options.GNU,
                 'solaris' : options.SOLARIS,
                 }

    # parse options
    dla opt, arg w opts:
        jeżeli opt w ('-h', '--help'):
            usage(0)
        albo_inaczej opt w ('-a', '--extract-all'):
            options.extractall = 1
        albo_inaczej opt w ('-d', '--default-domain'):
            options.outfile = arg + '.pot'
        albo_inaczej opt w ('-E', '--escape'):
            options.escape = 1
        albo_inaczej opt w ('-D', '--docstrings'):
            options.docstrings = 1
        albo_inaczej opt w ('-k', '--keyword'):
            options.keywords.append(arg)
        albo_inaczej opt w ('-K', '--no-default-keywords'):
            default_keywords = []
        albo_inaczej opt w ('-n', '--add-location'):
            options.writelocations = 1
        albo_inaczej opt w ('--no-location',):
            options.writelocations = 0
        albo_inaczej opt w ('-S', '--style'):
            options.locationstyle = locations.get(arg.lower())
            jeżeli options.locationstyle jest Nic:
                usage(1, _('Invalid value dla --style: %s') % arg)
        albo_inaczej opt w ('-o', '--output'):
            options.outfile = arg
        albo_inaczej opt w ('-p', '--output-dir'):
            options.outpath = arg
        albo_inaczej opt w ('-v', '--verbose'):
            options.verbose = 1
        albo_inaczej opt w ('-V', '--version'):
            print(_('pygettext.py (xgettext dla Python) %s') % __version__)
            sys.exit(0)
        albo_inaczej opt w ('-w', '--width'):
            spróbuj:
                options.width = int(arg)
            wyjąwszy ValueError:
                usage(1, _('--width argument must be an integer: %s') % arg)
        albo_inaczej opt w ('-x', '--exclude-file'):
            options.excludefilename = arg
        albo_inaczej opt w ('-X', '--no-docstrings'):
            fp = open(arg)
            spróbuj:
                dopóki 1:
                    line = fp.readline()
                    jeżeli nie line:
                        przerwij
                    options.nodocstrings[line[:-1]] = 1
            w_końcu:
                fp.close()

    # calculate escapes
    make_escapes(nie options.escape)

    # calculate all keywords
    options.keywords.extend(default_keywords)

    # initialize list of strings to exclude
    jeżeli options.excludefilename:
        spróbuj:
            fp = open(options.excludefilename)
            options.toexclude = fp.readlines()
            fp.close()
        wyjąwszy IOError:
            print(_(
                "Can't read --exclude-file: %s") % options.excludefilename, file=sys.stderr)
            sys.exit(1)
    inaczej:
        options.toexclude = []

    # resolve args to module lists
    expanded = []
    dla arg w args:
        jeżeli arg == '-':
            expanded.append(arg)
        inaczej:
            expanded.extend(getFilesForName(arg))
    args = expanded

    # slurp through all the files
    eater = TokenEater(options)
    dla filename w args:
        jeżeli filename == '-':
            jeżeli options.verbose:
                print(_('Reading standard input'))
            fp = sys.stdin.buffer
            closep = 0
        inaczej:
            jeżeli options.verbose:
                print(_('Working on %s') % filename)
            fp = open(filename, 'rb')
            closep = 1
        spróbuj:
            eater.set_filename(filename)
            spróbuj:
                tokens = tokenize.tokenize(fp.readline)
                dla _token w tokens:
                    eater(*_token)
            wyjąwszy tokenize.TokenError jako e:
                print('%s: %s, line %d, column %d' % (
                    e.args[0], filename, e.args[1][0], e.args[1][1]),
                    file=sys.stderr)
        w_końcu:
            jeżeli closep:
                fp.close()

    # write the output
    jeżeli options.outfile == '-':
        fp = sys.stdout
        closep = 0
    inaczej:
        jeżeli options.outpath:
            options.outfile = os.path.join(options.outpath, options.outfile)
        fp = open(options.outfile, 'w')
        closep = 1
    spróbuj:
        eater.write(fp)
    w_końcu:
        jeżeli closep:
            fp.close()


jeżeli __name__ == '__main__':
    main()
    # some more test strings
    # this one creates a warning
    _('*** Seen unexpected token "%(token)s"') % {'token': 'test'}
    _('more' 'than' 'one' 'string')
