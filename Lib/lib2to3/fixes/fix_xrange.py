# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes xrange(...) into range(...)."""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, consuming_calls
z .. zaimportuj patcomp


klasa FixXrange(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
              power<
                 (name='range'|name='xrange') trailer< '(' args=any ')' >
              rest=any* >
              """

    def start_tree(self, tree, filename):
        super(FixXrange, self).start_tree(tree, filename)
        self.transformed_xranges = set()

    def finish_tree(self, tree, filename):
        self.transformed_xranges = Nic

    def transform(self, node, results):
        name = results["name"]
        jeżeli name.value == "xrange":
            zwróć self.transform_xrange(node, results)
        albo_inaczej name.value == "range":
            zwróć self.transform_range(node, results)
        inaczej:
            podnieś ValueError(repr(name))

    def transform_xrange(self, node, results):
        name = results["name"]
        name.replace(Name("range", prefix=name.prefix))
        # This prevents the new range call z being wrapped w a list later.
        self.transformed_xranges.add(id(node))

    def transform_range(self, node, results):
        jeżeli (id(node) nie w self.transformed_xranges oraz
            nie self.in_special_context(node)):
            range_call = Call(Name("range"), [results["args"].clone()])
            # Encase the range call w list().
            list_call = Call(Name("list"), [range_call],
                             prefix=node.prefix)
            # Put things that were after the range() call after the list call.
            dla n w results["rest"]:
                list_call.append_child(n)
            zwróć list_call

    P1 = "power< func=NAME trailer< '(' node=any ')' > any* >"
    p1 = patcomp.compile_pattern(P1)

    P2 = """for_stmt< 'for' any 'in' node=any ':' any* >
            | comp_for< 'for' any 'in' node=any any* >
            | comparison< any 'in' node=any any*>
         """
    p2 = patcomp.compile_pattern(P2)

    def in_special_context(self, node):
        jeżeli node.parent jest Nic:
            zwróć Nieprawda
        results = {}
        jeżeli (node.parent.parent jest nie Nic oraz
               self.p1.match(node.parent.parent, results) oraz
               results["node"] jest node):
            # list(d.keys()) -> list(d.keys()), etc.
            zwróć results["func"].value w consuming_calls
        # dla ... w d.iterkeys() -> dla ... w d.keys(), etc.
        zwróć self.p2.match(node.parent, results) oraz results["node"] jest node
