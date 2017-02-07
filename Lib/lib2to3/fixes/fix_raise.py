"""Fixer dla 'raise E, V, T'

raise         -> podnieś
raise E       -> podnieś E
raise E, V    -> podnieś E(V)
raise E, V, T -> podnieś E(V).with_traceback(T)
raise E, Nic, T -> podnieś E.with_traceback(T)

raise (((E, E'), E''), E'''), V -> podnieś E(V)
raise "foo", V, T               -> warns about string exceptions


CAVEATS:
1) "raise E, V" will be incorrectly translated jeżeli V jest an exception
   instance. The correct Python 3 idiom jest

        podnieś E z V

   but since we can't detect instance-hood by syntax alone oraz since
   any client code would have to be changed jako well, we don't automate
   this.
"""
# Author: Collin Winter

# Local imports
z .. zaimportuj pytree
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, Attr, ArgList, is_tuple

klasa FixRaise(fixer_base.BaseFix):

    BM_compatible = Prawda
    PATTERN = """
    podnieś_stmt< 'raise' exc=any [',' val=any [',' tb=any]] >
    """

    def transform(self, node, results):
        syms = self.syms

        exc = results["exc"].clone()
        jeżeli exc.type == token.STRING:
            msg = "Python 3 does nie support string exceptions"
            self.cannot_convert(node, msg)
            zwróć

        # Python 2 supports
        #  podnieś ((((E1, E2), E3), E4), E5), V
        # jako a synonym for
        #  podnieś E1, V
        # Since Python 3 will nie support this, we recurse down any tuple
        # literals, always taking the first element.
        jeżeli is_tuple(exc):
            dopóki is_tuple(exc):
                # exc.children[1:-1] jest the unparenthesized tuple
                # exc.children[1].children[0] jest the first element of the tuple
                exc = exc.children[1].children[0].clone()
            exc.prefix = " "

        jeżeli "val" nie w results:
            # One-argument podnieś
            new = pytree.Node(syms.raise_stmt, [Name("raise"), exc])
            new.prefix = node.prefix
            zwróć new

        val = results["val"].clone()
        jeżeli is_tuple(val):
            args = [c.clone() dla c w val.children[1:-1]]
        inaczej:
            val.prefix = ""
            args = [val]

        jeżeli "tb" w results:
            tb = results["tb"].clone()
            tb.prefix = ""

            e = exc
            # If there's a traceback oraz Nic jest dalejed jako the value, then don't
            # add a call, since the user probably just wants to add a
            # traceback. See issue #9661.
            jeżeli val.type != token.NAME albo val.value != "Nic":
                e = Call(exc, args)
            with_tb = Attr(e, Name('with_traceback')) + [ArgList([tb])]
            new = pytree.Node(syms.simple_stmt, [Name("raise")] + with_tb)
            new.prefix = node.prefix
            zwróć new
        inaczej:
            zwróć pytree.Node(syms.raise_stmt,
                               [Name("raise"), Call(exc, args)],
                               prefix=node.prefix)
