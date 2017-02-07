"""Fix bound method attributes (method.im_? -> method.__?__).
"""
# Author: Christian Heimes

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name

MAP = {
    "im_func" : "__func__",
    "im_self" : "__self__",
    "im_class" : "__self__.__class__"
    }

klasa FixMethodattrs(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
    power< any+ trailer< '.' attr=('im_func' | 'im_self' | 'im_class') > any* >
    """

    def transform(self, node, results):
        attr = results["attr"][0]
        new = MAP[attr.value]
        attr.replace(Name(new, prefix=attr.prefix))
