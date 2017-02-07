"""Fixer that addes parentheses where they are required

This converts ``[x dla x w 1, 2]`` to ``[x dla x w (1, 2)]``."""

# By Taek Joo Kim oraz Benjamin Peterson

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj LParen, RParen

# XXX This doesn't support nested dla loops like [x dla x w 1, 2 dla x w 1, 2]
klasa FixParen(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
        atom< ('[' | '(')
            (listmaker< any
                comp_for<
                    'for' NAME 'in'
                    target=testlist_safe< any (',' any)+ [',']
                     >
                    [any]
                >
            >
            |
            testlist_gexp< any
                comp_for<
                    'for' NAME 'in'
                    target=testlist_safe< any (',' any)+ [',']
                     >
                    [any]
                >
            >)
        (']' | ')') >
    """

    def transform(self, node, results):
        target = results["target"]

        lparen = LParen()
        lparen.prefix = target.prefix
        target.prefix = "" # Make it hug the parentheses
        target.insert_child(0, lparen)
        target.append_child(RParen())
