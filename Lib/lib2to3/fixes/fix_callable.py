# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla callable().

This converts callable(obj) into isinstance(obj, collections.Callable), adding a
collections zaimportuj jeżeli needed."""

# Local imports
z lib2to3 zaimportuj fixer_base
z lib2to3.fixer_util zaimportuj Call, Name, String, Attr, touch_import

klasa FixCallable(fixer_base.BaseFix):
    BM_compatible = Prawda

    order = "pre"

    # Ignore callable(*args) albo use of keywords.
    # Either could be a hint that the builtin callable() jest nie being used.
    PATTERN = """
    power< 'callable'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) func=any
                      | func=arglist<(nie argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    def transform(self, node, results):
        func = results['func']

        touch_import(Nic, 'collections', node=node)

        args = [func.clone(), String(', ')]
        args.extend(Attr(Name('collections'), Name('Callable')))
        zwróć Call(Name('isinstance'), args, prefix=node.prefix)
