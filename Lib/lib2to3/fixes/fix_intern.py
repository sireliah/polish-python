# Copyright 2006 Georg Brandl.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla intern().

intern(s) -> sys.intern(s)"""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj ImportAndCall, touch_import


klasa FixIntern(fixer_base.BaseFix):
    BM_compatible = Prawda
    order = "pre"

    PATTERN = """
    power< 'intern'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) obj=any
                      | obj=arglist<(nie argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    def transform(self, node, results):
        names = ('sys', 'intern')
        new = ImportAndCall(node, results, names)
        touch_import(Nic, 'sys', node)
        zwróć new
