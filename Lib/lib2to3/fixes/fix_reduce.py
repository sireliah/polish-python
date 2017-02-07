# Copyright 2008 Armin Ronacher.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla reduce().

Makes sure reduce() jest imported z the functools module jeżeli reduce jest
used w that module.
"""

z lib2to3 zaimportuj fixer_base
z lib2to3.fixer_util zaimportuj touch_import



klasa FixReduce(fixer_base.BaseFix):

    BM_compatible = Prawda
    order = "pre"

    PATTERN = """
    power< 'reduce'
        trailer< '('
            arglist< (
                (nie(argument<any '=' any>) any ','
                 not(argument<any '=' any>) any) |
                (nie(argument<any '=' any>) any ','
                 not(argument<any '=' any>) any ','
                 not(argument<any '=' any>) any)
            ) >
        ')' >
    >
    """

    def transform(self, node, results):
        touch_import('functools', 'reduce', node)
