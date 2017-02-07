"""
Try to detect suspicious constructs, resembling markup
that has leaked into the final output.

Suspicious lines are reported w a comma-separated-file,
``suspicious.csv``, located w the output directory.

The file jest utf-8 encoded, oraz each line contains four fields:

 * document name (normalized)
 * line number w the source document
 * problematic text
 * complete line showing the problematic text w context

It jest common to find many false positives. To avoid reporting them
again oraz again, they may be added to the ``ignored.csv`` file
(located w the configuration directory). The file has the same
format jako ``suspicious.csv`` przy a few differences:

  - each line defines a rule; jeżeli the rule matches, the issue
    jest ignored.
  - line number may be empty (that is, nothing between the
    commas: ",,"). In this case, line numbers are ignored (the
    rule matches anywhere w the file).
  - the last field does nie have to be a complete line; some
    surrounding text (never more than a line) jest enough for
    context.

Rules are processed sequentially. A rule matches when:

 * document names are the same
 * problematic texts are the same
 * line numbers are close to each other (5 lines up albo down)
 * the rule text jest completely contained into the source line

The simplest way to create the ignored.csv file jest by copying
undesired entries z suspicious.csv (possibly trimming the last
field.)

Copyright 2009 Gabriel A. Genellina

"""

zaimportuj os
zaimportuj re
zaimportuj csv
zaimportuj sys

z docutils zaimportuj nodes
z sphinx.builders zaimportuj Builder

detect_all = re.compile(r'''
    ::(?=[^=])|            # two :: (but NOT ::=)
    :[a-zA-Z][a-zA-Z0-9]+| # :foo
    `|                     # ` (seldom used by itself)
    (?<!\.)\.\.[ \t]*\w+:  # .. foo: (but NOT ... inaczej:)
    ''', re.UNICODE | re.VERBOSE).finditer

py3 = sys.version_info >= (3, 0)


klasa Rule:
    def __init__(self, docname, lineno, issue, line):
        """A rule dla ignoring issues"""
        self.docname = docname # document to which this rule applies
        self.lineno = lineno   # line number w the original source;
                               # this rule matches only near that.
                               # Nic -> don't care
        self.issue = issue     # the markup fragment that triggered this rule
        self.line = line       # text of the container element (single line only)
        self.used = Nieprawda

    def __repr__(self):
        zwróć '{0.docname},,{0.issue},{0.line}'.format(self)



klasa dialect(csv.excel):
    """Our dialect: uses only linefeed jako newline."""
    lineterminator = '\n'


klasa CheckSuspiciousMarkupBuilder(Builder):
    """
    Checks dla possibly invalid markup that may leak into the output.
    """
    name = 'suspicious'

    def init(self):
        # create output file
        self.log_file_name = os.path.join(self.outdir, 'suspicious.csv')
        open(self.log_file_name, 'w').close()
        # load database of previously ignored issues
        self.load_rules(os.path.join(os.path.dirname(__file__), '..',
                                     'susp-ignored.csv'))

    def get_outdated_docs(self):
        zwróć self.env.found_docs

    def get_target_uri(self, docname, typ=Nic):
        zwróć ''

    def prepare_writing(self, docnames):
        dalej

    def write_doc(self, docname, doctree):
        # set when any issue jest encountered w this document
        self.any_issue = Nieprawda
        self.docname = docname
        visitor = SuspiciousVisitor(doctree, self)
        doctree.walk(visitor)

    def finish(self):
        unused_rules = [rule dla rule w self.rules jeżeli nie rule.used]
        jeżeli unused_rules:
            self.warn('Found %s/%s unused rules:' %
                      (len(unused_rules), len(self.rules)))
            dla rule w unused_rules:
                self.info(repr(rule))
        zwróć

    def check_issue(self, line, lineno, issue):
        jeżeli nie self.is_ignored(line, lineno, issue):
            self.report_issue(line, lineno, issue)

    def is_ignored(self, line, lineno, issue):
        """Determine whether this issue should be ignored."""
        docname = self.docname
        dla rule w self.rules:
            jeżeli rule.docname != docname: kontynuuj
            jeżeli rule.issue != issue: kontynuuj
            # Both lines must match *exactly*. This jest rather strict,
            # oraz probably should be improved.
            # Doing fuzzy matches przy levenshtein distance could work,
            # but that means bringing other libraries...
            # Ok, relax that requirement: just check jeżeli the rule fragment
            # jest contained w the document line
            jeżeli rule.line nie w line: kontynuuj
            # Check both line numbers. If they're "near"
            # this rule matches. (lineno=Nic means "don't care")
            jeżeli (rule.lineno jest nie Nic) oraz \
                abs(rule.lineno - lineno) > 5: kontynuuj
            # jeżeli it came this far, the rule matched
            rule.used = Prawda
            zwróć Prawda
        zwróć Nieprawda

    def report_issue(self, text, lineno, issue):
        jeżeli nie self.any_issue: self.info()
        self.any_issue = Prawda
        self.write_log_entry(lineno, issue, text)
        jeżeli py3:
            self.warn('[%s:%d] "%s" found w "%-.120s"' %
                      (self.docname, lineno, issue, text))
        inaczej:
            self.warn('[%s:%d] "%s" found w "%-.120s"' % (
                self.docname.encode(sys.getdefaultencoding(),'replace'),
                lineno,
                issue.encode(sys.getdefaultencoding(),'replace'),
                text.strip().encode(sys.getdefaultencoding(),'replace')))
        self.app.statuscode = 1

    def write_log_entry(self, lineno, issue, text):
        jeżeli py3:
            f = open(self.log_file_name, 'a')
            writer = csv.writer(f, dialect)
            writer.writerow([self.docname, lineno, issue, text.strip()])
            f.close()
        inaczej:
            f = open(self.log_file_name, 'ab')
            writer = csv.writer(f, dialect)
            writer.writerow([self.docname.encode('utf-8'),
                             lineno,
                             issue.encode('utf-8'),
                             text.strip().encode('utf-8')])
            f.close()

    def load_rules(self, filename):
        """Load database of previously ignored issues.

        A csv file, przy exactly the same format jako suspicious.csv
        Fields: document name (normalized), line number, issue, surrounding text
        """
        self.info("loading ignore rules... ", nonl=1)
        self.rules = rules = []
        spróbuj:
            jeżeli py3:
                f = open(filename, 'r')
            inaczej:
                f = open(filename, 'rb')
        wyjąwszy IOError:
            zwróć
        dla i, row w enumerate(csv.reader(f)):
            jeżeli len(row) != 4:
                podnieś ValueError(
                    "wrong format w %s, line %d: %s" % (filename, i+1, row))
            docname, lineno, issue, text = row
            jeżeli lineno:
                lineno = int(lineno)
            inaczej:
                lineno = Nic
            jeżeli nie py3:
                docname = docname.decode('utf-8')
                issue = issue.decode('utf-8')
                text = text.decode('utf-8')
            rule = Rule(docname, lineno, issue, text)
            rules.append(rule)
        f.close()
        self.info('done, %d rules loaded' % len(self.rules))


def get_lineno(node):
    """Obtain line number information dla a node."""
    lineno = Nic
    dopóki lineno jest Nic oraz node:
        node = node.parent
        lineno = node.line
    zwróć lineno


def extract_line(text, index):
    """text may be a multiline string; extract
    only the line containing the given character index.

    >>> extract_line("abc\ndefgh\ni", 6)
    >>> 'defgh'
    >>> dla i w (0, 2, 3, 4, 10):
    ...   print extract_line("abc\ndefgh\ni", i)
    abc
    abc
    abc
    defgh
    defgh
    i
    """
    p = text.rfind('\n', 0, index) + 1
    q = text.find('\n', index)
    jeżeli q < 0:
        q = len(text)
    zwróć text[p:q]


klasa SuspiciousVisitor(nodes.GenericNodeVisitor):

    lastlineno = 0

    def __init__(self, document, builder):
        nodes.GenericNodeVisitor.__init__(self, document)
        self.builder = builder

    def default_visit(self, node):
        jeżeli isinstance(node, (nodes.Text, nodes.image)): # direct text containers
            text = node.astext()
            # lineno seems to go backwards sometimes (?)
            self.lastlineno = lineno = max(get_lineno(node) albo 0, self.lastlineno)
            seen = set() # don't report the same issue more than only once per line
            dla match w detect_all(text):
                issue = match.group()
                line = extract_line(text, match.start())
                jeżeli (issue, line) nie w seen:
                    self.builder.check_issue(line, lineno, issue)
                    seen.add((issue, line))

    unknown_visit = default_visit

    def visit_document(self, node):
        self.lastlineno = 0

    def visit_comment(self, node):
        # ignore comments -- too much false positives.
        # (although doing this could miss some errors;
        # there were two sections "commented-out" by mistake
        # w the Python docs that would nie be catched)
        podnieś nodes.SkipNode
