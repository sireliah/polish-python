# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that turns <> into !=."""

# Local imports
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base


klasa FixNe(fixer_base.BaseFix):
    # This jest so simple that we don't need the pattern compiler.

    _accept_type = token.NOTEQUAL

    def match(self, node):
        # Override
        zwróć node.value == "<>"

    def transform(self, node, results):
        new = pytree.Leaf(token.NOTEQUAL, "!=", prefix=node.prefix)
        zwróć new
