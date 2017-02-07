# -*- coding: utf-8 -*-
"""
    pyspecific.py
    ~~~~~~~~~~~~~

    Sphinx extension przy Python doc-specific markup.

    :copyright: 2008-2014 by Georg Brandl.
    :license: Python license.
"""

zaimportuj re
zaimportuj codecs
z os zaimportuj path
z time zaimportuj asctime
z pprint zaimportuj pformat
z docutils.io zaimportuj StringOutput
z docutils.utils zaimportuj new_document

z docutils zaimportuj nodes, utils

z sphinx zaimportuj addnodes
z sphinx.builders zaimportuj Builder
z sphinx.util.nodes zaimportuj split_explicit_title
z sphinx.util.compat zaimportuj Directive
z sphinx.writers.html zaimportuj HTMLTranslator
z sphinx.writers.text zaimportuj TextWriter
z sphinx.writers.latex zaimportuj LaTeXTranslator
z sphinx.domains.python zaimportuj PyModulelevel, PyClassmember

# Support dla checking dla suspicious markup

zaimportuj suspicious


ISSUE_URI = 'https://bugs.python.org/issue%s'
SOURCE_URI = 'https://hg.python.org/cpython/file/3.5/%s'

# monkey-patch reST parser to disable alphabetic oraz roman enumerated lists
z docutils.parsers.rst.states zaimportuj Body
Body.enum.converters['loweralpha'] = \
    Body.enum.converters['upperalpha'] = \
    Body.enum.converters['lowerroman'] = \
    Body.enum.converters['upperroman'] = lambda x: Nic

# monkey-patch HTML oraz LaTeX translators to keep doctest blocks w the
# doctest docs themselves
orig_visit_literal_block = HTMLTranslator.visit_literal_block
orig_depart_literal_block = LaTeXTranslator.depart_literal_block


def new_visit_literal_block(self, node):
    meta = self.builder.env.metadata[self.builder.current_docname]
    old_trim_doctest_flags = self.highlighter.trim_doctest_flags
    jeżeli 'keepdoctest' w meta:
        self.highlighter.trim_doctest_flags = Nieprawda
    spróbuj:
        orig_visit_literal_block(self, node)
    w_końcu:
        self.highlighter.trim_doctest_flags = old_trim_doctest_flags


def new_depart_literal_block(self, node):
    meta = self.builder.env.metadata[self.curfilestack[-1]]
    old_trim_doctest_flags = self.highlighter.trim_doctest_flags
    jeżeli 'keepdoctest' w meta:
        self.highlighter.trim_doctest_flags = Nieprawda
    spróbuj:
        orig_depart_literal_block(self, node)
    w_końcu:
        self.highlighter.trim_doctest_flags = old_trim_doctest_flags


HTMLTranslator.visit_literal_block = new_visit_literal_block
LaTeXTranslator.depart_literal_block = new_depart_literal_block


# Support dla marking up oraz linking to bugs.python.org issues

def issue_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    issue = utils.unescape(text)
    text = 'issue ' + issue
    refnode = nodes.reference(text, text, refuri=ISSUE_URI % issue)
    zwróć [refnode], []


# Support dla linking to Python source files easily

def source_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    has_t, title, target = split_explicit_title(text)
    title = utils.unescape(title)
    target = utils.unescape(target)
    refnode = nodes.reference(title, title, refuri=SOURCE_URI % target)
    zwróć [refnode], []


# Support dla marking up implementation details

klasa ImplementationDetail(Directive):

    has_content = Prawda
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = Prawda

    def run(self):
        pnode = nodes.compound(classes=['impl-detail'])
        content = self.content
        add_text = nodes.strong('CPython implementation detail:',
                                'CPython implementation detail:')
        jeżeli self.arguments:
            n, m = self.state.inline_text(self.arguments[0], self.lineno)
            pnode.append(nodes.paragraph('', '', *(n + m)))
        self.state.nested_parse(content, self.content_offset, pnode)
        jeżeli pnode.children oraz isinstance(pnode[0], nodes.paragraph):
            pnode[0].insert(0, add_text)
            pnode[0].insert(1, nodes.Text(' '))
        inaczej:
            pnode.insert(0, nodes.paragraph('', '', add_text))
        zwróć [pnode]


# Support dla documenting decorators

klasa PyDecoratorMixin(object):
    def handle_signature(self, sig, signode):
        ret = super(PyDecoratorMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_addname('@', '@'))
        zwróć ret

    def needs_arglist(self):
        zwróć Nieprawda


klasa PyDecoratorFunction(PyDecoratorMixin, PyModulelevel):
    def run(self):
        # a decorator function jest a function after all
        self.name = 'py:function'
        zwróć PyModulelevel.run(self)


klasa PyDecoratorMethod(PyDecoratorMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        zwróć PyClassmember.run(self)


klasa PyCoroutineMixin(object):
    def handle_signature(self, sig, signode):
        ret = super(PyCoroutineMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('coroutine ', 'coroutine '))
        zwróć ret


klasa PyCoroutineFunction(PyCoroutineMixin, PyModulelevel):
    def run(self):
        self.name = 'py:function'
        zwróć PyModulelevel.run(self)


klasa PyCoroutineMethod(PyCoroutineMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        zwróć PyClassmember.run(self)


# Support dla documenting version of removal w deprecations

klasa DeprecatedRemoved(Directive):
    has_content = Prawda
    required_arguments = 2
    optional_arguments = 1
    final_argument_whitespace = Prawda
    option_spec = {}

    _label = 'Deprecated since version %s, will be removed w version %s'

    def run(self):
        node = addnodes.versionmodified()
        node.document = self.state.document
        node['type'] = 'deprecated-removed'
        version = (self.arguments[0], self.arguments[1])
        node['version'] = version
        text = self._label % version
        jeżeli len(self.arguments) == 3:
            inodes, messages = self.state.inline_text(self.arguments[2],
                                                      self.lineno+1)
            para = nodes.paragraph(self.arguments[2], '', *inodes)
            node.append(para)
        inaczej:
            messages = []
        jeżeli self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        jeżeli len(node):
            jeżeli isinstance(node[0], nodes.paragraph) oraz node[0].rawsource:
                content = nodes.inline(node[0].rawsource, translatable=Prawda)
                content.source = node[0].source
                content.line = node[0].line
                content += node[0].children
                node[0].replace_self(nodes.paragraph('', '', content))
            node[0].insert(0, nodes.inline('', '%s: ' % text,
                                           classes=['versionmodified']))
        inaczej:
            para = nodes.paragraph('', '',
                                   nodes.inline('', '%s.' % text,
                                                classes=['versionmodified']))
            node.append(para)
        env = self.state.document.settings.env
        env.note_versionchange('deprecated', version[0], node, self.lineno)
        zwróć [node] + messages


# Support dla including Misc/NEWS

issue_re = re.compile('([Ii])ssue #([0-9]+)')
whatsnew_re = re.compile(r"(?im)^what's new w (.*?)\??$")


klasa MiscNews(Directive):
    has_content = Nieprawda
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = Nieprawda
    option_spec = {}

    def run(self):
        fname = self.arguments[0]
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        source_dir = path.dirname(path.abspath(source))
        fpath = path.join(source_dir, fname)
        self.state.document.settings.record_dependencies.add(fpath)
        spróbuj:
            fp = codecs.open(fpath, encoding='utf-8')
            spróbuj:
                content = fp.read()
            w_końcu:
                fp.close()
        wyjąwszy Exception:
            text = 'The NEWS file jest nie available.'
            node = nodes.strong(text, text)
            zwróć [node]
        content = issue_re.sub(r'`\1ssue #\2 <https://bugs.python.org/\2>`__',
                               content)
        content = whatsnew_re.sub(r'\1', content)
        # remove first 3 lines jako they are the main heading
        lines = ['.. default-role:: obj', ''] + content.splitlines()[3:]
        self.state_machine.insert_input(lines, fname)
        zwróć []


# Support dla building "topic help" dla pydoc

pydoc_topic_labels = [
    'assert', 'assignment', 'atom-identifiers', 'atom-literals',
    'attribute-access', 'attribute-references', 'augassign', 'binary',
    'bitwise', 'bltin-code-objects', 'bltin-ellipsis-object',
    'bltin-null-object', 'bltin-type-objects', 'booleans',
    'break', 'callable-types', 'calls', 'class', 'comparisons', 'compound',
    'context-managers', 'continue', 'conversions', 'customization', 'debugger',
    'del', 'dict', 'dynamic-features', 'inaczej', 'exceptions', 'execmodel',
    'exprlists', 'floating', 'for', 'formatstrings', 'function', 'global',
    'id-classes', 'identifiers', 'if', 'imaginary', 'import', 'in', 'integers',
    'lambda', 'lists', 'naming', 'nonlocal', 'numbers', 'numeric-types',
    'objects', 'operator-summary', 'pass', 'power', 'raise', 'return',
    'sequence-types', 'shifting', 'slicings', 'specialattrs', 'specialnames',
    'string-methods', 'strings', 'subscriptions', 'truth', 'try', 'types',
    'typesfunctions', 'typesmapping', 'typesmethods', 'typesmodules',
    'typesseq', 'typesseq-mutable', 'unary', 'while', 'with', 'uzyskaj'
]


klasa PydocTopicsBuilder(Builder):
    name = 'pydoc-topics'

    def init(self):
        self.topics = {}

    def get_outdated_docs(self):
        zwróć 'all pydoc topics'

    def get_target_uri(self, docname, typ=Nic):
        zwróć ''  # no URIs

    def write(self, *ignored):
        writer = TextWriter(self)
        dla label w self.status_iterator(pydoc_topic_labels,
                                          'building topics... ',
                                          length=len(pydoc_topic_labels)):
            jeżeli label nie w self.env.domaindata['std']['labels']:
                self.warn('label %r nie w documentation' % label)
                kontynuuj
            docname, labelid, sectname = self.env.domaindata['std']['labels'][label]
            doctree = self.env.get_and_resolve_doctree(docname, self)
            document = new_document('<section node>')
            document.append(doctree.ids[labelid])
            destination = StringOutput(encoding='utf-8')
            writer.write(document, destination)
            self.topics[label] = writer.output

    def finish(self):
        f = open(path.join(self.outdir, 'topics.py'), 'wb')
        spróbuj:
            f.write('# -*- coding: utf-8 -*-\n'.encode('utf-8'))
            f.write(('# Autogenerated by Sphinx on %s\n' % asctime()).encode('utf-8'))
            f.write(('topics = ' + pformat(self.topics) + '\n').encode('utf-8'))
        w_końcu:
            f.close()


# Support dla documenting Opcodes

opcode_sig_re = re.compile(r'(\w+(?:\+\d)?)(?:\s*\((.*)\))?')


def parse_opcode_signature(env, sig, signode):
    """Transform an opcode signature into RST nodes."""
    m = opcode_sig_re.match(sig)
    jeżeli m jest Nic:
        podnieś ValueError
    opname, arglist = m.groups()
    signode += addnodes.desc_name(opname, opname)
    jeżeli arglist jest nie Nic:
        paramlist = addnodes.desc_parameterlist()
        signode += paramlist
        paramlist += addnodes.desc_parameter(arglist, arglist)
    zwróć opname.strip()


# Support dla documenting pdb commands

pdbcmd_sig_re = re.compile(r'([a-z()!]+)\s*(.*)')

# later...
# pdbargs_tokens_re = re.compile(r'''[a-zA-Z]+  |  # identifiers
#                                   [.,:]+     |  # punctuation
#                                   [\[\]()]   |  # parens
#                                   \s+           # whitespace
#                                   ''', re.X)


def parse_pdb_command(env, sig, signode):
    """Transform a pdb command signature into RST nodes."""
    m = pdbcmd_sig_re.match(sig)
    jeżeli m jest Nic:
        podnieś ValueError
    name, args = m.groups()
    fullname = name.replace('(', '').replace(')', '')
    signode += addnodes.desc_name(name, name)
    jeżeli args:
        signode += addnodes.desc_addname(' '+args, ' '+args)
    zwróć fullname


def setup(app):
    app.add_role('issue', issue_role)
    app.add_role('source', source_role)
    app.add_directive('impl-detail', ImplementationDetail)
    app.add_directive('deprecated-removed', DeprecatedRemoved)
    app.add_builder(PydocTopicsBuilder)
    app.add_builder(suspicious.CheckSuspiciousMarkupBuilder)
    app.add_description_unit('opcode', 'opcode', '%s (opcode)',
                             parse_opcode_signature)
    app.add_description_unit('pdbcommand', 'pdbcmd', '%s (pdb command)',
                             parse_pdb_command)
    app.add_description_unit('2to3fixer', '2to3fixer', '%s (2to3 fixer)')
    app.add_directive_to_domain('py', 'decorator', PyDecoratorFunction)
    app.add_directive_to_domain('py', 'decoratormethod', PyDecoratorMethod)
    app.add_directive_to_domain('py', 'coroutinefunction', PyCoroutineFunction)
    app.add_directive_to_domain('py', 'coroutinemethod', PyCoroutineMethod)
    app.add_directive('miscnews', MiscNews)
    zwróć {'version': '1.0', 'parallel_read_safe': Prawda}
