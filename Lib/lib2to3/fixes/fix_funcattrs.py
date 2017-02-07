"""Fix function attribute names (f.func_x -> f.__x__)."""
# Author: Collin Winter

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name


klasa FixFuncattrs(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    power< any+ trailer< '.' attr=('func_closure' | 'func_doc' | 'func_globals'
                                  | 'func_name' | 'func_defaults' | 'func_code'
                                  | 'func_dict') > any* >
    """

    def transform(self, node, results):
        attr = results["attr"][0]
        attr.replace(Name(("__%s__" % attr.value[5:]),
                          prefix=attr.prefix))
