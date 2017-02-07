# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla has_key().

Calls to .has_key() methods are expressed w terms of the 'in'
operator:

    d.has_key(k) -> k w d

CAVEATS:
1) While the primary target of this fixer jest dict.has_key(), the
   fixer will change any has_key() method call, regardless of its
   class.

2) Cases like this will nie be converted:

    m = d.has_key
    jeżeli m(k):
        ...

   Only *calls* to has_key() are converted. While it jest possible to
   convert the above to something like

    m = d.__contains__
    jeżeli m(k):
        ...

   this jest currently nie done.
"""

# Local imports
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, parenthesize


klasa FixHasKey(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    anchor=power<
        before=any+
        trailer< '.' 'has_key' >
        trailer<
            '('
            ( not(arglist | argument<any '=' any>) arg=any
            | arglist<(nie argument<any '=' any>) arg=any ','>
            )
            ')'
        >
        after=any*
    >
    |
    negation=not_test<
        'not'
        anchor=power<
            before=any+
            trailer< '.' 'has_key' >
            trailer<
                '('
                ( not(arglist | argument<any '=' any>) arg=any
                | arglist<(nie argument<any '=' any>) arg=any ','>
                )
                ')'
            >
        >
    >
    """

    def transform(self, node, results):
        assert results
        syms = self.syms
        jeżeli (node.parent.type == syms.not_test oraz
            self.pattern.match(node.parent)):
            # Don't transform a node matching the first alternative of the
            # pattern when its parent matches the second alternative
            zwróć Nic
        negation = results.get("negation")
        anchor = results["anchor"]
        prefix = node.prefix
        before = [n.clone() dla n w results["before"]]
        arg = results["arg"].clone()
        after = results.get("after")
        jeżeli after:
            after = [n.clone() dla n w after]
        jeżeli arg.type w (syms.comparison, syms.not_test, syms.and_test,
                        syms.or_test, syms.test, syms.lambdef, syms.argument):
            arg = parenthesize(arg)
        jeżeli len(before) == 1:
            before = before[0]
        inaczej:
            before = pytree.Node(syms.power, before)
        before.prefix = " "
        n_op = Name("in", prefix=" ")
        jeżeli negation:
            n_not = Name("not", prefix=" ")
            n_op = pytree.Node(syms.comp_op, (n_not, n_op))
        new = pytree.Node(syms.comparison, (arg, n_op, before))
        jeżeli after:
            new = parenthesize(new)
            new = pytree.Node(syms.power, (new,) + tuple(after))
        jeżeli node.parent.type w (syms.comparison, syms.expr, syms.xor_expr,
                                syms.and_expr, syms.shift_expr,
                                syms.arith_expr, syms.term,
                                syms.factor, syms.power):
            new = parenthesize(new)
        new.prefix = prefix
        zwróć new
