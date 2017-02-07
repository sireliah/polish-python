"""Fix incompatible renames

Fixes:
  * sys.maxint -> sys.maxsize
"""
# Author: Christian Heimes
# based on Collin Winter's fix_import

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, attr_chain

MAPPING = {"sys":  {"maxint" : "maxsize"},
          }
LOOKUP = {}

def alternates(members):
    zwróć "(" + "|".join(map(repr, members)) + ")"


def build_pattern():
    #bare = set()
    dla module, replace w list(MAPPING.items()):
        dla old_attr, new_attr w list(replace.items()):
            LOOKUP[(module, old_attr)] = new_attr
            #bare.add(module)
            #bare.add(old_attr)
            #uzyskaj """
            #      import_name< 'import' (module=%r
            #          | dotted_as_names< any* module=%r any* >) >
            #      """ % (module, module)
            uzyskaj """
                  import_from< 'from' module_name=%r 'import'
                      ( attr_name=%r | import_as_name< attr_name=%r 'as' any >) >
                  """ % (module, old_attr, old_attr)
            uzyskaj """
                  power< module_name=%r trailer< '.' attr_name=%r > any* >
                  """ % (module, old_attr)
    #uzyskaj """bare_name=%s""" % alternates(bare)


klasa FixRenames(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = "|".join(build_pattern())

    order = "pre" # Pre-order tree traversal

    # Don't match the node jeżeli it's within another match
    def match(self, node):
        match = super(FixRenames, self).match
        results = match(node)
        jeżeli results:
            jeżeli any(match(obj) dla obj w attr_chain(node, "parent")):
                zwróć Nieprawda
            zwróć results
        zwróć Nieprawda

    #def start_tree(self, tree, filename):
    #    super(FixRenames, self).start_tree(tree, filename)
    #    self.replace = {}

    def transform(self, node, results):
        mod_name = results.get("module_name")
        attr_name = results.get("attr_name")
        #bare_name = results.get("bare_name")
        #import_mod = results.get("module")

        jeżeli mod_name oraz attr_name:
            new_attr = LOOKUP[(mod_name.value, attr_name.value)]
            attr_name.replace(Name(new_attr, prefix=attr_name.prefix))
