# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes buffer(...) into memoryview(...)."""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name


klasa FixBuffer(fixer_base.BaseFix):
    BM_compatible = Prawda

    explicit = Prawda # The user must ask dla this fixer

    PATTERN = """
              power< name='buffer' trailer< '(' [any] ')' > any* >
              """

    def transform(self, node, results):
        name = results["name"]
        name.replace(Name("memoryview", prefix=name.prefix))
