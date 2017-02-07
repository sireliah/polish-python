# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that turns 'long' into 'int' everywhere.
"""

# Local imports
z lib2to3 zaimportuj fixer_base
z lib2to3.fixer_util zaimportuj is_probably_builtin


klasa FixLong(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = "'long'"

    def transform(self, node, results):
        jeżeli is_probably_builtin(node):
            node.value = "int"
            node.changed()
