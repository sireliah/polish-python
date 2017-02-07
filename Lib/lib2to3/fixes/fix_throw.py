"""Fixer dla generator.throw(E, V, T).

g.throw(E)       -> g.throw(E)
g.throw(E, V)    -> g.throw(E(V))
g.throw(E, V, T) -> g.throw(E(V).with_traceback(T))

g.throw("foo"[, V[, T]]) will warn about string exceptions."""
# Author: Collin Winter

# Local imports
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, ArgList, Attr, is_tuple

klasa FixThrow(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
    power< any trailer< '.' 'throw' >
           trailer< '(' args=arglist< exc=any ',' val=any [',' tb=any] > ')' >
    >
    |
    power< any trailer< '.' 'throw' > trailer< '(' exc=any ')' > >
    """

    def transform(self, node, results):
        syms = self.syms

        exc = results["exc"].clone()
        jeżeli exc.type jest token.STRING:
            self.cannot_convert(node, "Python 3 does nie support string exceptions")
            zwróć

        # Leave "g.throw(E)" alone
        val = results.get("val")
        jeżeli val jest Nic:
            zwróć

        val = val.clone()
        jeżeli is_tuple(val):
            args = [c.clone() dla c w val.children[1:-1]]
        inaczej:
            val.prefix = ""
            args = [val]

        throw_args = results["args"]

        jeżeli "tb" w results:
            tb = results["tb"].clone()
            tb.prefix = ""

            e = Call(exc, args)
            with_tb = Attr(e, Name('with_traceback')) + [ArgList([tb])]
            throw_args.replace(pytree.Node(syms.power, with_tb))
        inaczej:
            throw_args.replace(Call(exc, args))
