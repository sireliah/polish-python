# Copyright 2008 Armin Ronacher.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that cleans up a tuple argument to isinstance after the tokens
in it were fixed.  This jest mainly used to remove double occurrences of
tokens jako a leftover of the long -> int / unicode -> str conversion.

eg.  isinstance(x, (int, long)) -> isinstance(x, (int, int))
       -> isinstance(x, int)
"""

z .. zaimportuj fixer_base
z ..fixer_util zaimportuj token


klasa FixIsinstance(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = """
    power<
        'isinstance'
        trailer< '(' arglist< any ',' atom< '('
            args=testlist_gexp< any+ >
        ')' > > ')' >
    >
    """

    run_order = 6

    def transform(self, node, results):
        names_inserted = set()
        testlist = results["args"]
        args = testlist.children
        new_args = []
        iterator = enumerate(args)
        dla idx, arg w iterator:
            jeżeli arg.type == token.NAME oraz arg.value w names_inserted:
                jeżeli idx < len(args) - 1 oraz args[idx + 1].type == token.COMMA:
                    next(iterator)
                    kontynuuj
            inaczej:
                new_args.append(arg)
                jeżeli arg.type == token.NAME:
                    names_inserted.add(arg.value)
        jeżeli new_args oraz new_args[-1].type == token.COMMA:
            usuń new_args[-1]
        jeżeli len(new_args) == 1:
            atom = testlist.parent
            new_args[0].prefix = atom.prefix
            atom.replace(new_args[0])
        inaczej:
            args[:] = new_args
            node.changed()
