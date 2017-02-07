"""Fixer that changes raw_input(...) into input(...)."""
# Author: Andre Roberge

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name

klasa FixRawInput(fixer_base.BaseFix):

    BM_compatible = Prawda
    PATTERN = """
              power< name='raw_input' trailer< '(' [any] ')' > any* >
              """

    def transform(self, node, results):
        name = results["name"]
        name.replace(Name("input", prefix=name.prefix))
