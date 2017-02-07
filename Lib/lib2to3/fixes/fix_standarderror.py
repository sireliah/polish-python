# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla StandardError -> Exception."""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name


klasa FixStandarderror(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
              'StandardError'
              """

    def transform(self, node, results):
        zwróć Name("Exception", prefix=node.prefix)
