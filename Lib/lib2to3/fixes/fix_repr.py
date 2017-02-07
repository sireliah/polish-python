# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that transforms `xyzzy` into repr(xyzzy)."""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Call, Name, parenthesize


klasa FixRepr(fixer_base.BaseFix):

    BM_compatible = Prawda
    PATTERN = """
              atom < '`' expr=any '`' >
              """

    def transform(self, node, results):
        expr = results["expr"].clone()

        jeżeli expr.type == self.syms.testlist1:
            expr = parenthesize(expr)
        zwróć Call(Name("repr"), [expr], prefix=node.prefix)
