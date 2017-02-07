# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Export the Python grammar oraz symbols."""

# Python imports
zaimportuj os

# Local imports
z .pgen2 zaimportuj token
z .pgen2 zaimportuj driver
z . zaimportuj pytree

# The grammar file
_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")
_PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__),
                                     "PatternGrammar.txt")


klasa Symbols(object):

    def __init__(self, grammar):
        """Initializer.

        Creates an attribute dla each grammar symbol (nonterminal),
        whose value jest the symbol's type (an int >= 256).
        """
        dla name, symbol w grammar.symbol2number.items():
            setattr(self, name, symbol)


python_grammar = driver.load_grammar(_GRAMMAR_FILE)

python_symbols = Symbols(python_grammar)

python_grammar_no_print_statement = python_grammar.copy()
usuń python_grammar_no_print_statement.keywords["print"]

pattern_grammar = driver.load_grammar(_PATTERN_GRAMMAR_FILE)
pattern_symbols = Symbols(pattern_grammar)
