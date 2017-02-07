#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Check dla stylistic oraz formal issues w .rst oraz .py
# files included w the documentation.
#
# 01/2009, Georg Brandl

# TODO: - wrong versions w versionadded/changed
#       - wrong markup after versionchanged directive

z __future__ zaimportuj with_statement

zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj getopt
z os.path zaimportuj join, splitext, abspath, exists
z collections zaimportuj defaultdict

directives = [
    # standard docutils ones
    'admonition', 'attention', 'caution', 'class', 'compound', 'container',
    'contents', 'csv-table', 'danger', 'date', 'default-role', 'epigraph',
    'error', 'figure', 'footer', 'header', 'highlights', 'hint', 'image',
    'important', 'include', 'line-block', 'list-table', 'meta', 'note',
    'parsed-literal', 'pull-quote', 'raw', 'replace',
    'restructuredtext-test-directive', 'role', 'rubric', 'sectnum', 'sidebar',
    'table', 'target-notes', 'tip', 'title', 'topic', 'unicode', 'warning',
    # Sphinx oraz Python docs custom ones
    'acks', 'attribute', 'autoattribute', 'autoclass', 'autodata',
    'autoexception', 'autofunction', 'automethod', 'automodule', 'centered',
    'cfunction', 'class', 'classmethod', 'cmacro', 'cmdoption', 'cmember',
    'code-block', 'confval', 'cssclass', 'ctype', 'currentmodule', 'cvar',
    'data', 'decorator', 'decoratormethod', 'deprecated-removed',
    'deprecated(?!-removed)', 'describe', 'directive', 'doctest', 'envvar',
    'event', 'exception', 'function', 'glossary', 'highlight', 'highlightlang',
    'impl-detail', 'index', 'literalinclude', 'method', 'miscnews', 'module',
    'moduleauthor', 'opcode', 'pdbcommand', 'productionlist',
    'program', 'role', 'sectionauthor', 'seealso', 'sourcecode', 'staticmethod',
    'tabularcolumns', 'testcode', 'testoutput', 'testsetup', 'toctree', 'todo',
    'todolist', 'versionadded', 'versionchanged'
]

all_directives = '(' + '|'.join(directives) + ')'
seems_directive_re = re.compile(r'\.\. %s([^a-z:]|:(?!:))' % all_directives)
default_role_re = re.compile(r'(^| )`\w([^`]*?\w)?`($| )')
leaked_markup_re = re.compile(r'[a-z]::\s|`|\.\.\s*\w+:')


checkers = {}

checker_props = {'severity': 1, 'falsepositives': Nieprawda}


def checker(*suffixes, **kwds):
    """Decorator to register a function jako a checker."""
    def deco(func):
        dla suffix w suffixes:
            checkers.setdefault(suffix, []).append(func)
        dla prop w checker_props:
            setattr(func, prop, kwds.get(prop, checker_props[prop]))
        zwróć func
    zwróć deco


@checker('.py', severity=4)
def check_syntax(fn, lines):
    """Check Python examples dla valid syntax."""
    code = ''.join(lines)
    jeżeli '\r' w code:
        jeżeli os.name != 'nt':
            uzyskaj 0, '\\r w code file'
        code = code.replace('\r', '')
    spróbuj:
        compile(code, fn, 'exec')
    wyjąwszy SyntaxError jako err:
        uzyskaj err.lineno, 'not compilable: %s' % err


@checker('.rst', severity=2)
def check_suspicious_constructs(fn, lines):
    """Check dla suspicious reST constructs."""
    inprod = Nieprawda
    dla lno, line w enumerate(lines):
        jeżeli seems_directive_re.match(line):
            uzyskaj lno+1, 'comment seems to be intended jako a directive'
        jeżeli '.. productionlist::' w line:
            inprod = Prawda
        albo_inaczej nie inprod oraz default_role_re.search(line):
            uzyskaj lno+1, 'default role used'
        albo_inaczej inprod oraz nie line.strip():
            inprod = Nieprawda


@checker('.py', '.rst')
def check_whitespace(fn, lines):
    """Check dla whitespace oraz line length issues."""
    dla lno, line w enumerate(lines):
        jeżeli '\r' w line:
            uzyskaj lno+1, '\\r w line'
        jeżeli '\t' w line:
            uzyskaj lno+1, 'OMG TABS!!!1'
        jeżeli line[:-1].rstrip(' \t') != line[:-1]:
            uzyskaj lno+1, 'trailing whitespace'


@checker('.rst', severity=0)
def check_line_length(fn, lines):
    """Check dla line length; this checker jest nie run by default."""
    dla lno, line w enumerate(lines):
        jeżeli len(line) > 81:
            # don't complain about tables, links oraz function signatures
            jeżeli line.lstrip()[0] nie w '+|' oraz \
               'http://' nie w line oraz \
               nie line.lstrip().startswith(('.. function',
                                             '.. method',
                                             '.. cfunction')):
                uzyskaj lno+1, "line too long"


@checker('.html', severity=2, falsepositives=Prawda)
def check_leaked_markup(fn, lines):
    """Check HTML files dla leaked reST markup; this only works if
    the HTML files have been built.
    """
    dla lno, line w enumerate(lines):
        jeżeli leaked_markup_re.search(line):
            uzyskaj lno+1, 'possibly leaked markup: %r' % line


def main(argv):
    usage = '''\
Usage: %s [-v] [-f] [-s sev] [-i path]* [path]

Options:  -v       verbose (print all checked file names)
          -f       enable checkers that uzyskaj many false positives
          -s sev   only show problems przy severity >= sev
          -i path  ignore subdir albo file path
''' % argv[0]
    spróbuj:
        gopts, args = getopt.getopt(argv[1:], 'vfs:i:')
    wyjąwszy getopt.GetoptError:
        print(usage)
        zwróć 2

    verbose = Nieprawda
    severity = 1
    ignore = []
    falsepos = Nieprawda
    dla opt, val w gopts:
        jeżeli opt == '-v':
            verbose = Prawda
        albo_inaczej opt == '-f':
            falsepos = Prawda
        albo_inaczej opt == '-s':
            severity = int(val)
        albo_inaczej opt == '-i':
            ignore.append(abspath(val))

    jeżeli len(args) == 0:
        path = '.'
    albo_inaczej len(args) == 1:
        path = args[0]
    inaczej:
        print(usage)
        zwróć 2

    jeżeli nie exists(path):
        print('Error: path %s does nie exist' % path)
        zwróć 2

    count = defaultdict(int)

    dla root, dirs, files w os.walk(path):
        # ignore subdirs w ignore list
        jeżeli abspath(root) w ignore:
            usuń dirs[:]
            kontynuuj

        dla fn w files:
            fn = join(root, fn)
            jeżeli fn[:2] == './':
                fn = fn[2:]

            # ignore files w ignore list
            jeżeli abspath(fn) w ignore:
                kontynuuj

            ext = splitext(fn)[1]
            checkerlist = checkers.get(ext, Nic)
            jeżeli nie checkerlist:
                kontynuuj

            jeżeli verbose:
                print('Checking %s...' % fn)

            spróbuj:
                przy open(fn, 'r', encoding='utf-8') jako f:
                    lines = list(f)
            wyjąwszy (IOError, OSError) jako err:
                print('%s: cannot open: %s' % (fn, err))
                count[4] += 1
                kontynuuj

            dla checker w checkerlist:
                jeżeli checker.falsepositives oraz nie falsepos:
                    kontynuuj
                csev = checker.severity
                jeżeli csev >= severity:
                    dla lno, msg w checker(fn, lines):
                        print('[%d] %s:%d: %s' % (csev, fn, lno, msg))
                        count[csev] += 1
    jeżeli verbose:
        print()
    jeżeli nie count:
        jeżeli severity > 1:
            print('No problems przy severity >= %d found.' % severity)
        inaczej:
            print('No problems found.')
    inaczej:
        dla severity w sorted(count):
            number = count[severity]
            print('%d problem%s przy severity %d found.' %
                  (number, number > 1 oraz 's' albo '', severity))
    zwróć int(bool(count))


jeżeli __name__ == '__main__':
    sys.exit(main(sys.argv))
