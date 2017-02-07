"""Fixer dla basestring -> str."""
# Author: Christian Heimes

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name

klasa FixBasestring(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = "'basestring'"

    def transform(self, node, results):
        zwróć Name("str", prefix=node.prefix)
