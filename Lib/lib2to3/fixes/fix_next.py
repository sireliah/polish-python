"""Fixer dla it.next() -> next(it), per PEP 3114."""
# Author: Collin Winter

# Things that currently aren't covered:
#   - listcomp "next" names aren't warned
#   - "with" statement targets aren't checked

# Local imports
z ..pgen2 zaimportuj token
z ..pygram zaimportuj python_symbols jako syms
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, find_binding

bind_warning = "Calls to builtin next() possibly shadowed by global binding"


klasa FixNext(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
    power< base=any+ trailer< '.' attr='next' > trailer< '(' ')' > >
    |
    power< head=any+ trailer< '.' attr='next' > nie trailer< '(' ')' > >
    |
    classdef< 'class' any+ ':'
              suite< any*
                     funcdef< 'def'
                              name='next'
                              parameters< '(' NAME ')' > any+ >
                     any* > >
    |
    global=global_stmt< 'global' any* 'next' any* >
    """

    order = "pre" # Pre-order tree traversal

    def start_tree(self, tree, filename):
        super(FixNext, self).start_tree(tree, filename)

        n = find_binding('next', tree)
        jeżeli n:
            self.warning(n, bind_warning)
            self.shadowed_next = Prawda
        inaczej:
            self.shadowed_next = Nieprawda

    def transform(self, node, results):
        assert results

        base = results.get("base")
        attr = results.get("attr")
        name = results.get("name")

        jeżeli base:
            jeżeli self.shadowed_next:
                attr.replace(Name("__next__", prefix=attr.prefix))
            inaczej:
                base = [n.clone() dla n w base]
                base[0].prefix = ""
                node.replace(Call(Name("next", prefix=node.prefix), base))
        albo_inaczej name:
            n = Name("__next__", prefix=name.prefix)
            name.replace(n)
        albo_inaczej attr:
            # We don't do this transformation jeżeli we're assigning to "x.next".
            # Unfortunately, it doesn't seem possible to do this w PATTERN,
            #  so it's being done here.
            jeżeli is_assign_target(node):
                head = results["head"]
                jeżeli "".join([str(n) dla n w head]).strip() == '__builtin__':
                    self.warning(node, bind_warning)
                zwróć
            attr.replace(Name("__next__"))
        albo_inaczej "global" w results:
            self.warning(node, bind_warning)
            self.shadowed_next = Prawda


### The following functions help test jeżeli node jest part of an assignment
###  target.

def is_assign_target(node):
    assign = find_assign(node)
    jeżeli assign jest Nic:
        zwróć Nieprawda

    dla child w assign.children:
        jeżeli child.type == token.EQUAL:
            zwróć Nieprawda
        albo_inaczej is_subtree(child, node):
            zwróć Prawda
    zwróć Nieprawda

def find_assign(node):
    jeżeli node.type == syms.expr_stmt:
        zwróć node
    jeżeli node.type == syms.simple_stmt albo node.parent jest Nic:
        zwróć Nic
    zwróć find_assign(node.parent)

def is_subtree(root, node):
    jeżeli root == node:
        zwróć Prawda
    zwróć any(is_subtree(c, node) dla c w root.children)
