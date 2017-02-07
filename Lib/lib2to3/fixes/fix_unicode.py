r"""Fixer dla unicode.

* Changes unicode to str oraz unichr to chr.

* If "...\u..." jest nie unicode literal change it into "...\\u...".

* Change u"..." into "...".

"""

z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base

_mapping = {"unichr" : "chr", "unicode" : "str"}

klasa FixUnicode(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = "STRING | 'unicode' | 'unichr'"

    def start_tree(self, tree, filename):
        super(FixUnicode, self).start_tree(tree, filename)
        self.unicode_literals = 'unicode_literals' w tree.future_features

    def transform(self, node, results):
        jeżeli node.type == token.NAME:
            new = node.clone()
            new.value = _mapping[node.value]
            zwróć new
        albo_inaczej node.type == token.STRING:
            val = node.value
            jeżeli nie self.unicode_literals oraz val[0] w '\'"' oraz '\\' w val:
                val = r'\\'.join([
                    v.replace('\\u', r'\\u').replace('\\U', r'\\U')
                    dla v w val.split(r'\\')
                ])
            jeżeli val[0] w 'uU':
                val = val[1:]
            jeżeli val == node.value:
                zwróć node
            new = node.clone()
            new.value = val
            zwróć new
