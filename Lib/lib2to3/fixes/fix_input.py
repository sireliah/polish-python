"""Fixer that changes input(...) into eval(input(...))."""
# Author: Andre Roberge

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Call, Name
z .. zaimportuj patcomp


context = patcomp.compile_pattern("power< 'eval' trailer< '(' any ')' > >")


klasa FixInput(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
              power< 'input' args=trailer< '(' [any] ')' > >
              """

    def transform(self, node, results):
        # If we're already wrapped w a eval() call, we're done.
        jeżeli context.match(node.parent.parent):
            zwróć

        new = node.clone()
        new.prefix = ""
        zwróć Call(Name("eval"), [new], prefix=node.prefix)
