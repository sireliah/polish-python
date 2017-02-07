# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla exec.

This converts usages of the exec statement into calls to a built-in
exec() function.

exec code w ns1, ns2 -> exec(code, ns1, ns2)
"""

# Local imports
z .. zaimportuj pytree
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Comma, Name, Call


klasa FixExec(fixer_base.BaseFix):
    BM_compatible = Prawda

    PATTERN = """
    exec_stmt< 'exec' a=any 'in' b=any [',' c=any] >
    |
    exec_stmt< 'exec' (nie atom<'(' [any] ')'>) a=any >
    """

    def transform(self, node, results):
        assert results
        syms = self.syms
        a = results["a"]
        b = results.get("b")
        c = results.get("c")
        args = [a.clone()]
        args[0].prefix = ""
        jeżeli b jest nie Nic:
            args.extend([Comma(), b.clone()])
        jeżeli c jest nie Nic:
            args.extend([Comma(), c.clone()])

        zwróć Call(Name("exec"), args, prefix=node.prefix)
