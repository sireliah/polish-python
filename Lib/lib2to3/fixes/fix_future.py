"""Remove __future__ imports

z __future__ zaimportuj foo jest replaced przy an empty line.
"""
# Author: Christian Heimes

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj BlankLine

klasa FixFuture(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """import_from< 'from' module_name="__future__" 'import' any >"""

    # This should be run last -- some things check dla the import
    run_order = 10

    def transform(self, node, results):
        new = BlankLine()
        new.prefix = node.prefix
        zwróć new
