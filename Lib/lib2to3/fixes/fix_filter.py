# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes filter(F, X) into list(filter(F, X)).

We avoid the transformation jeżeli the filter() call jest directly contained
in iter(<>), list(<>), tuple(<>), sorted(<>), ...join(<>), albo
dla V w <>:.

NOTE: This jest still nie correct jeżeli the original code was depending on
filter(F, X) to zwróć a string jeżeli X jest a string oraz a tuple jeżeli X jest a
tuple.  That would require type inference, which we don't do.  Let
Python 2.6 figure it out.
"""

# Local imports
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, ListComp, in_special_context

klasa FixFilter(fixer_base.ConditionalFix):
    BM_compatible = Prawda

    PATTERN = """
    filter_lambda=power<
        'filter'
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
        'filter'
        trailer< '(' arglist< none='Nic' ',' seq=any > ')' >
    >
    |
    power<
        'filter'
        args=trailer< '(' [any] ')' >
    >
    """

    skip_on = "future_builtins.filter"

    def transform(self, node, results):
        jeżeli self.should_skip(node):
            zwróć

        jeżeli "filter_lambda" w results:
            new = ListComp(results.get("fp").clone(),
                           results.get("fp").clone(),
                           results.get("it").clone(),
                           results.get("xp").clone())

        albo_inaczej "none" w results:
            new = ListComp(Name("_f"),
                           Name("_f"),
                           results["seq"].clone(),
                           Name("_f"))

        inaczej:
            jeżeli in_special_context(node):
                zwróć Nic
            new = node.clone()
            new.prefix = ""
            new = Call(Name("list"), [new])
        new.prefix = node.prefix
        zwróć new
