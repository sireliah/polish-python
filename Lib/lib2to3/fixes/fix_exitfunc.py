"""
Convert use of sys.exitfunc to use the atexit module.
"""

# Author: Benjamin Peterson

z lib2to3 zaimportuj pytree, fixer_base
z lib2to3.fixer_util zaimportuj Name, Attr, Call, Comma, Newline, syms


klasa FixExitfunc(fixer_base.BaseFix):
    keep_line_order = Prawda
    BM_compatible = Prawda

    PATTERN = """
              (
                  sys_import=import_name<'import'
                      ('sys'
                      |
                      dotted_as_names< (any ',')* 'sys' (',' any)* >
                      )
                  >
              |
                  expr_stmt<
                      power< 'sys' trailer< '.' 'exitfunc' > >
                  '=' func=any >
              )
              """

    def __init__(self, *args):
        super(FixExitfunc, self).__init__(*args)

    def start_tree(self, tree, filename):
        super(FixExitfunc, self).start_tree(tree, filename)
        self.sys_zaimportuj = Nic

    def transform(self, node, results):
        # First, find the sys import. We'll just hope it's global scope.
        jeżeli "sys_import" w results:
            jeżeli self.sys_zaimportuj jest Nic:
                self.sys_zaimportuj = results["sys_import"]
            zwróć

        func = results["func"].clone()
        func.prefix = ""
        register = pytree.Node(syms.power,
                               Attr(Name("atexit"), Name("register"))
                               )
        call = Call(register, [func], node.prefix)
        node.replace(call)

        jeżeli self.sys_zaimportuj jest Nic:
            # That's interesting.
            self.warning(node, "Can't find sys import; Please add an atexit "
                             "zaimportuj at the top of your file.")
            zwróć

        # Now add an atexit zaimportuj after the sys import.
        names = self.sys_import.children[1]
        jeżeli names.type == syms.dotted_as_names:
            names.append_child(Comma())
            names.append_child(Name("atexit", " "))
        inaczej:
            containing_stmt = self.sys_import.parent
            position = containing_stmt.children.index(self.sys_import)
            stmt_container = containing_stmt.parent
            new_zaimportuj = pytree.Node(syms.import_name,
                              [Name("import"), Name("atexit", " ")]
                              )
            new = pytree.Node(syms.simple_stmt, [new_import])
            containing_stmt.insert_child(position + 1, Newline())
            containing_stmt.insert_child(position + 2, new)
