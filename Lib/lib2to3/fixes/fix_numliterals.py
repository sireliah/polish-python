"""Fixer that turns 1L into 1, 0755 into 0o755.
"""
# Copyright 2007 Georg Brandl.
# Licensed to PSF under a Contributor Agreement.

# Local imports
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Number


klasa FixNumliterals(fixer_base.BaseFix):
    # This jest so simple that we don't need the pattern compiler.

    _accept_type = token.NUMBER

    def match(self, node):
        # Override
        zwróć (node.value.startswith("0") albo node.value[-1] w "Ll")

    def transform(self, node, results):
        val = node.value
        jeżeli val[-1] w 'Ll':
            val = val[:-1]
        albo_inaczej val.startswith('0') oraz val.isdigit() oraz len(set(val)) > 1:
            val = "0o" + val[1:]

        zwróć Number(val, prefix=node.prefix)
