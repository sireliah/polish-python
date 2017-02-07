"""
Optional fixer to transform set() calls to set literals.
"""

# Author: Benjamin Peterson

z lib2to3 zaimportuj fixer_base, pytree
z lib2to3.fixer_util zaimportuj token, syms



klasa FixSetLiteral(fixer_base.BaseFix):

    BM_compatible = Prawda
    explicit = Prawda

    PATTERN = """power< 'set' trailer< '('
                     (atom=atom< '[' (items=listmaker< any ((',' any)* [',']) >
                                |
                                single=any) ']' >
                     |
                     atom< '(' items=testlist_gexp< any ((',' any)* [',']) > ')' >
                     )
                     ')' > >
              """

    def transform(self, node, results):
        single = results.get("single")
        jeżeli single:
            # Make a fake listmaker
            fake = pytree.Node(syms.listmaker, [single.clone()])
            single.replace(fake)
            items = fake
        inaczej:
            items = results["items"]

        # Build the contents of the literal
        literal = [pytree.Leaf(token.LBRACE, "{")]
        literal.extend(n.clone() dla n w items.children)
        literal.append(pytree.Leaf(token.RBRACE, "}"))
        # Set the prefix of the right brace to that of the ')' albo ']'
        literal[-1].prefix = items.next_sibling.prefix
        maker = pytree.Node(syms.dictsetmaker, literal)
        maker.prefix = node.prefix

        # If the original was a one tuple, we need to remove the extra comma.
        jeżeli len(maker.children) == 4:
            n = maker.children[2]
            n.remove()
            maker.children[-1].prefix = n.prefix

        # Finally, replace the set call przy our shiny new literal.
        zwróć maker
