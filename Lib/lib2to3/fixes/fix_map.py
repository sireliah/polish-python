# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes map(F, ...) into list(map(F, ...)) unless there
exists a 'z future_builtins zaimportuj map' statement w the top-level
namespace.

As a special case, map(Nic, X) jest changed into list(X).  (This jest
necessary because the semantics are changed w this case -- the new
map(Nic, X) jest equivalent to [(x,) dla x w X].)

We avoid the transformation (wyjąwszy dla the special case mentioned
above) jeżeli the map() call jest directly contained w iter(<>), list(<>),
tuple(<>), sorted(<>), ...join(<>), albo dla V w <>:.

NOTE: This jest still nie correct jeżeli the original code was depending on
map(F, X, Y, ...) to go on until the longest argument jest exhausted,
substituting Nic dla missing values -- like zip(), it now stops as
soon jako the shortest argument jest exhausted.
"""

# Local imports
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, ListComp, in_special_context
z ..pygram zaimportuj python_symbols jako syms

klasa FixMap(fixer_base.ConditionalFix):
    BM_compatible = Prawda

    PATTERN = """
    map_none=power<
        'map'
        trailer< '(' arglist< 'Nic' ',' arg=any [','] > ')' >
    >
    |
    map_lambda=power<
        'map'
        trailer<
            '('
            arglist<
                lambdef< 'lambda'
                         (fp=NAME | vfpdef< '(' fp=NAME ')'> ) ':' xp=any
                >
                ','
                it=any
            >
            ')'
        >
    >
    |
    power<
        'map' trailer< '(' [arglist=any] ')' >
    >
    """

    skip_on = 'future_builtins.map'

    def transform(self, node, results):
        jeżeli self.should_skip(node):
            zwróć

        jeżeli node.parent.type == syms.simple_stmt:
            self.warning(node, "You should use a dla loop here")
            new = node.clone()
            new.prefix = ""
            new = Call(Name("list"), [new])
        albo_inaczej "map_lambda" w results:
            new = ListComp(results["xp"].clone(),
                           results["fp"].clone(),
                           results["it"].clone())
        inaczej:
            jeżeli "map_none" w results:
                new = results["arg"].clone()
            inaczej:
                jeżeli "arglist" w results:
                    args = results["arglist"]
                    jeżeli args.type == syms.arglist oraz \
                       args.children[0].type == token.NAME oraz \
                       args.children[0].value == "Nic":
                        self.warning(node, "cannot convert map(Nic, ...) "
                                     "przy multiple arguments because map() "
                                     "now truncates to the shortest sequence")
                        zwróć
                jeżeli in_special_context(node):
                    zwróć Nic
                new = node.clone()
            new.prefix = ""
            new = Call(Name("list"), [new])
        new.prefix = node.prefix
        zwróć new
