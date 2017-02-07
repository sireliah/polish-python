# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla print.

Change:
    'print'          into 'print()'
    'print ...'      into 'print(...)'
    'print ... ,'    into 'print(..., end=" ")'
    'print >>x, ...' into 'print(..., file=x)'

No changes are applied jeżeli print_function jest imported z __future__

"""

# Local imports
z .. zaimportuj patcomp
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, Comma, String, is_tuple


parend_expr = patcomp.compile_pattern(
              """atom< '(' [atom|STRING|NAME] ')' >"""
              )


klasa FixPrint(fixer_base.BaseFix):

    BM_compatible = Prawda

    PATTERN = """
              simple_stmt< any* bare='print' any* > | print_stmt
              """

    def transform(self, node, results):
        assert results

        bare_print = results.get("bare")

        jeżeli bare_print:
            # Special-case print all by itself
            bare_print.replace(Call(Name("print"), [],
                               prefix=bare_print.prefix))
            zwróć
        assert node.children[0] == Name("print")
        args = node.children[1:]
        jeżeli len(args) == 1 oraz parend_expr.match(args[0]):
            # We don't want to keep sticking parens around an
            # already-parenthesised expression.
            zwróć

        sep = end = file = Nic
        jeżeli args oraz args[-1] == Comma():
            args = args[:-1]
            end = " "
        jeżeli args oraz args[0] == pytree.Leaf(token.RIGHTSHIFT, ">>"):
            assert len(args) >= 2
            file = args[1].clone()
            args = args[3:] # Strip a possible comma after the file expression
        # Now synthesize a print(args, sep=..., end=..., file=...) node.
        l_args = [arg.clone() dla arg w args]
        jeżeli l_args:
            l_args[0].prefix = ""
        jeżeli sep jest nie Nic albo end jest nie Nic albo file jest nie Nic:
            jeżeli sep jest nie Nic:
                self.add_kwarg(l_args, "sep", String(repr(sep)))
            jeżeli end jest nie Nic:
                self.add_kwarg(l_args, "end", String(repr(end)))
            jeżeli file jest nie Nic:
                self.add_kwarg(l_args, "file", file)
        n_stmt = Call(Name("print"), l_args)
        n_stmt.prefix = node.prefix
        zwróć n_stmt

    def add_kwarg(self, l_nodes, s_kwd, n_expr):
        # XXX All this prefix-setting may lose comments (though rarely)
        n_expr.prefix = ""
        n_argument = pytree.Node(self.syms.argument,
                                 (Name(s_kwd),
                                  pytree.Leaf(token.EQUAL, "="),
                                  n_expr))
        jeżeli l_nodes:
            l_nodes.append(Comma())
            n_argument.prefix = " "
        l_nodes.append(n_argument)
