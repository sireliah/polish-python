"""Fixer dla zaimportuj statements.
If spam jest being imported z the local directory, this import:
    z spam zaimportuj eggs
Becomes:
    z .spam zaimportuj eggs

And this import:
    zaimportuj spam
Becomes:
    z . zaimportuj spam
"""

# Local imports
z .. zaimportuj fixer_base
z os.path zaimportuj dirname, join, exists, sep
z ..fixer_util zaimportuj FromImport, syms, token


def traverse_imports(names):
    """
    Walks over all the names imported w a dotted_as_names node.
    """
    pending = [names]
    dopóki pending:
        node = pending.pop()
        jeżeli node.type == token.NAME:
            uzyskaj node.value
        albo_inaczej node.type == syms.dotted_name:
            uzyskaj "".join([ch.value dla ch w node.children])
        albo_inaczej node.type == syms.dotted_as_name:
            pending.append(node.children[0])
        albo_inaczej node.type == syms.dotted_as_names:
            pending.extend(node.children[::-2])
        inaczej:
            podnieś AssertionError("unknown node type")


klasa FixImport(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    import_from< 'from' imp=any 'import' ['('] any [')'] >
    |
    import_name< 'import' imp=any >
    """

    def start_tree(self, tree, name):
        super(FixImport, self).start_tree(tree, name)
        self.skip = "absolute_import" w tree.future_features

    def transform(self, node, results):
        jeżeli self.skip:
            zwróć
        imp = results['imp']

        jeżeli node.type == syms.import_from:
            # Some imps are top-level (eg: 'zaimportuj ham')
            # some are first level (eg: 'zaimportuj ham.eggs')
            # some are third level (eg: 'zaimportuj ham.eggs jako spam')
            # Hence, the loop
            dopóki nie hasattr(imp, 'value'):
                imp = imp.children[0]
            jeżeli self.probably_a_local_import(imp.value):
                imp.value = "." + imp.value
                imp.changed()
        inaczej:
            have_local = Nieprawda
            have_absolute = Nieprawda
            dla mod_name w traverse_imports(imp):
                jeżeli self.probably_a_local_import(mod_name):
                    have_local = Prawda
                inaczej:
                    have_absolute = Prawda
            jeżeli have_absolute:
                jeżeli have_local:
                    # We won't handle both sibling oraz absolute imports w the
                    # same statement at the moment.
                    self.warning(node, "absolute oraz local imports together")
                zwróć

            new = FromImport(".", [imp])
            new.prefix = node.prefix
            zwróć new

    def probably_a_local_import(self, imp_name):
        jeżeli imp_name.startswith("."):
            # Relative imports are certainly nie local imports.
            zwróć Nieprawda
        imp_name = imp_name.split(".", 1)[0]
        base_path = dirname(self.filename)
        base_path = join(base_path, imp_name)
        # If there jest no __init__.py next to the file its nie w a package
        # so can't be a relative import.
        jeżeli nie exists(join(dirname(base_path), "__init__.py")):
            zwróć Nieprawda
        dla ext w [".py", sep, ".pyc", ".so", ".sl", ".pyd"]:
            jeżeli exists(base_path + ext):
                zwróć Prawda
        zwróć Nieprawda
