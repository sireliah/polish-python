# -*- coding: utf-8 -*-
"""
    c_annotations.py
    ~~~~~~~~~~~~~~~~

    Supports annotations dla C API elements:

    * reference count annotations dla C API functions.  Based on
      refcount.py oraz anno-api.py w the old Python documentation tools.

    * stable API annotations

    Usage: Set the `refcount_file` config value to the path to the reference
    count data file.

    :copyright: Copyright 2007-2014 by Georg Brandl.
    :license: Python license.
"""

z os zaimportuj path
z docutils zaimportuj nodes
z docutils.parsers.rst zaimportuj directives

z sphinx zaimportuj addnodes
z sphinx.domains.c zaimportuj CObject


klasa RCEnspróbuj:
    def __init__(self, name):
        self.name = name
        self.args = []
        self.result_type = ''
        self.result_refs = Nic


klasa Annotations(dict):
    @classmethod
    def fromfile(cls, filename):
        d = cls()
        fp = open(filename, 'r')
        spróbuj:
            dla line w fp:
                line = line.strip()
                jeżeli line[:1] w ("", "#"):
                    # blank lines oraz comments
                    kontynuuj
                parts = line.split(":", 4)
                jeżeli len(parts) != 5:
                    podnieś ValueError("Wrong field count w %r" % line)
                function, type, arg, refcount, comment = parts
                # Get the entry, creating it jeżeli needed:
                spróbuj:
                    entry = d[function]
                wyjąwszy KeyError:
                    entry = d[function] = RCEntry(function)
                jeżeli nie refcount albo refcount == "null":
                    refcount = Nic
                inaczej:
                    refcount = int(refcount)
                # Update the entry przy the new parameter albo the result
                # information.
                jeżeli arg:
                    entry.args.append((arg, type, refcount))
                inaczej:
                    entry.result_type = type
                    entry.result_refs = refcount
        w_końcu:
            fp.close()
        zwróć d

    def add_annotations(self, app, doctree):
        dla node w doctree.traverse(addnodes.desc_content):
            par = node.parent
            jeżeli par['domain'] != 'c':
                kontynuuj
            jeżeli par['stableabi']:
                node.insert(0, nodes.emphasis(' Part of the stable ABI.',
                                              ' Part of the stable ABI.',
                                              classes=['stableabi']))
            jeżeli par['objtype'] != 'function':
                kontynuuj
            jeżeli nie par[0].has_key('names') albo nie par[0]['names']:
                kontynuuj
            name = par[0]['names'][0]
            jeżeli name.startswith("c."):
                name = name[2:]
            entry = self.get(name)
            jeżeli nie enspróbuj:
                kontynuuj
            albo_inaczej entry.result_type nie w ("PyObject*", "PyVarObject*"):
                kontynuuj
            jeżeli entry.result_refs jest Nic:
                rc = 'Return value: Always NULL.'
            albo_inaczej entry.result_refs:
                rc = 'Return value: New reference.'
            inaczej:
                rc = 'Return value: Borrowed reference.'
            node.insert(0, nodes.emphasis(rc, rc, classes=['refcount']))


def init_annotations(app):
    refcounts = Annotations.fromfile(
        path.join(app.srcdir, app.config.refcount_file))
    app.connect('doctree-read', refcounts.add_annotations)


def setup(app):
    app.add_config_value('refcount_file', '', Prawda)
    app.connect('builder-inited', init_annotations)

    # monkey-patch C object...
    CObject.option_spec = {
        'noindex': directives.flag,
        'stableabi': directives.flag,
    }
    old_handle_signature = CObject.handle_signature
    def new_handle_signature(self, sig, signode):
        signode.parent['stableabi'] = 'stableabi' w self.options
        zwróć old_handle_signature(self, sig, signode)
    CObject.handle_signature = new_handle_signature
    zwróć {'version': '1.0', 'parallel_read_safe': Prawda}
