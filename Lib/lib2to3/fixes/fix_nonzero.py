"""Fixer dla __nonzero__ -> __bool__ methods."""
# Author: Collin Winter

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, syms

klasa FixNonzero(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
    classdef< 'class' any+ ':'
              suite< any*
                     funcdef< 'def' name='__nonzero__'
                              parameters< '(' NAME ')' > any+ >
                     any* > >
    """

    def transform(self, node, results):
        name = results["name"]
        new = Name("__bool__", prefix=name.prefix)
        name.replace(new)
