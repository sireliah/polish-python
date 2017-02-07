"""Fix "dla x w f.xreadlines()" -> "dla x w f".

This fixer will also convert g(f.xreadlines) into g(f.__iter__)."""
# Author: Collin Winter

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name


klasa FixXreadlines(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
    power< call=any+ trailer< '.' 'xreadlines' > trailer< '(' ')' > >
    |
    power< any+ trailer< '.' no_call='xreadlines' > >
    """

    def transform(self, node, results):
        no_call = results.get("no_call")

        jeżeli no_call:
            no_call.replace(Name("__iter__", prefix=no_call.prefix))
        inaczej:
            node.replace([x.clone() dla x w results["call"]])
