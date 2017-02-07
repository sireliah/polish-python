# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla dict methods.

d.keys() -> list(d.keys())
d.items() -> list(d.items())
d.values() -> list(d.values())

d.iterkeys() -> iter(d.keys())
d.iteritems() -> iter(d.items())
d.itervalues() -> iter(d.values())

d.viewkeys() -> d.keys()
d.viewitems() -> d.items()
d.viewvalues() -> d.values()

Except w certain very specific contexts: the iter() can be dropped
when the context jest list(), sorted(), iter() albo for...in; the list()
can be dropped when the context jest list() albo sorted() (but nie iter()
or for...in!). Special contexts that apply to both: list(), sorted(), tuple()
set(), any(), all(), sum().

Note: iter(d.keys()) could be written jako iter(d) but since the
original d.iterkeys() was also redundant we don't fix this.  And there
are (rare) contexts where it makes a difference (e.g. when dalejing it
as an argument to a function that introspects the argument).
"""

# Local imports
z .. zaimportuj pytree
z .. zaimportuj patcomp
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, LParen, RParen, ArgList, Dot
z .. zaimportuj fixer_util


iter_exempt = fixer_util.consuming_calls | {"iter"}


klasa FixDict(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    power< head=any+
         trailer< '.' method=('keys'|'items'|'values'|
                              'iterkeys'|'iteritems'|'itervalues'|
                              'viewkeys'|'viewitems'|'viewvalues') >
         parens=trailer< '(' ')' >
         tail=any*
    >
    """

    def transform(self, node, results):
        head = results["head"]
        method = results["method"][0] # Extract node dla method name
        tail = results["tail"]
        syms = self.syms
        method_name = method.value
        isiter = method_name.startswith("iter")
        isview = method_name.startswith("view")
        jeżeli isiter albo isview:
            method_name = method_name[4:]
        assert method_name w ("keys", "items", "values"), repr(method)
        head = [n.clone() dla n w head]
        tail = [n.clone() dla n w tail]
        special = nie tail oraz self.in_special_context(node, isiter)
        args = head + [pytree.Node(syms.trailer,
                                   [Dot(),
                                    Name(method_name,
                                         prefix=method.prefix)]),
                       results["parens"].clone()]
        new = pytree.Node(syms.power, args)
        jeżeli nie (special albo isview):
            new.prefix = ""
            new = Call(Name("iter" jeżeli isiter inaczej "list"), [new])
        jeżeli tail:
            new = pytree.Node(syms.power, [new] + tail)
        new.prefix = node.prefix
        zwróć new

    P1 = "power< func=NAME trailer< '(' node=any ')' > any* >"
    p1 = patcomp.compile_pattern(P1)

    P2 = """for_stmt< 'for' any 'in' node=any ':' any* >
            | comp_for< 'for' any 'in' node=any any* >
         """
    p2 = patcomp.compile_pattern(P2)

    def in_special_context(self, node, isiter):
        jeżeli node.parent jest Nic:
            zwróć Nieprawda
        results = {}
        jeżeli (node.parent.parent jest nie Nic oraz
               self.p1.match(node.parent.parent, results) oraz
               results["node"] jest node):
            jeżeli isiter:
                # iter(d.iterkeys()) -> iter(d.keys()), etc.
                zwróć results["func"].value w iter_exempt
            inaczej:
                # list(d.keys()) -> list(d.keys()), etc.
                zwróć results["func"].value w fixer_util.consuming_calls
        jeżeli nie isiter:
            zwróć Nieprawda
        # dla ... w d.iterkeys() -> dla ... w d.keys(), etc.
        zwróć self.p2.match(node.parent, results) oraz results["node"] jest node
