"""Fixer dla reload().

reload(s) -> imp.reload(s)"""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj ImportAndCall, touch_import


klasa FixReload(fixer_base.BaseFix):
    BM_compatible = Prawda
    order = "pre"

    PATTERN = """
    power< 'reload'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) obj=any
                      | obj=arglist<(nie argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    def transform(self, node, results):
        names = ('imp', 'reload')
        new = ImportAndCall(node, results, names)
        touch_import(Nic, 'imp', node)
        zwróć new
