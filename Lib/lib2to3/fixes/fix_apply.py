# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla apply().

This converts apply(func, v, k) into (func)(*v, **k)."""

# Local imports
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Call, Comma, parenthesize

klasa FixApply(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    power< 'apply'
        trailer<
            '('
            arglist<
                (nie argument<NAME '=' any>) func=any ','
                (nie argument<NAME '=' any>) args=any [','
                (nie argument<NAME '=' any>) kwds=any] [',']
            >
            ')'
        >
    >
    """

    def transform(self, node, results):
        syms = self.syms
        assert results
        func = results["func"]
        args = results["args"]
        kwds = results.get("kwds")
        prefix = node.prefix
        func = func.clone()
        jeżeli (func.type nie w (token.NAME, syms.atom) oraz
            (func.type != syms.power albo
             func.children[-2].type == token.DOUBLESTAR)):
            # Need to parenthesize
            func = parenthesize(func)
        func.prefix = ""
        args = args.clone()
        args.prefix = ""
        jeżeli kwds jest nie Nic:
            kwds = kwds.clone()
            kwds.prefix = ""
        l_newargs = [pytree.Leaf(token.STAR, "*"), args]
        jeżeli kwds jest nie Nic:
            l_newargs.extend([Comma(),
                              pytree.Leaf(token.DOUBLESTAR, "**"),
                              kwds])
            l_newargs[-2].prefix = " " # that's the ** token
        # XXX Sometimes we could be cleverer, e.g. apply(f, (x, y) + t)
        # can be translated into f(x, y, *t) instead of f(*(x, y) + t)
        #new = pytree.Node(syms.power, (func, ArgList(l_newargs)))
        zwróć Call(func, l_newargs, prefix=prefix)
