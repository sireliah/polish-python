# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Pattern compiler.

The grammer jest taken z PatternGrammar.txt.

The compiler compiles a pattern to a pytree.*Pattern instance.
"""

__author__ = "Guido van Rossum <guido@python.org>"

# Python imports
zaimportuj io
zaimportuj os

# Fairly local imports
z .pgen2 zaimportuj driver, literals, token, tokenize, parse, grammar

# Really local imports
z . zaimportuj pytree
z . zaimportuj pygram

# The pattern grammar file
_PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__),
                                     "PatternGrammar.txt")


klasa PatternSyntaxError(Exception):
    dalej


def tokenize_wrapper(input):
    """Tokenizes a string suppressing significant whitespace."""
    skip = {token.NEWLINE, token.INDENT, token.DEDENT}
    tokens = tokenize.generate_tokens(io.StringIO(input).readline)
    dla quintuple w tokens:
        type, value, start, end, line_text = quintuple
        jeżeli type nie w skip:
            uzyskaj quintuple


klasa PatternCompiler(object):

    def __init__(self, grammar_file=_PATTERN_GRAMMAR_FILE):
        """Initializer.

        Takes an optional alternative filename dla the pattern grammar.
        """
        self.grammar = driver.load_grammar(grammar_file)
        self.syms = pygram.Symbols(self.grammar)
        self.pygrammar = pygram.python_grammar
        self.pysyms = pygram.python_symbols
        self.driver = driver.Driver(self.grammar, convert=pattern_convert)

    def compile_pattern(self, input, debug=Nieprawda, with_tree=Nieprawda):
        """Compiles a pattern string to a nested pytree.*Pattern object."""
        tokens = tokenize_wrapper(input)
        spróbuj:
            root = self.driver.parse_tokens(tokens, debug=debug)
        wyjąwszy parse.ParseError jako e:
            podnieś PatternSyntaxError(str(e))
        jeżeli with_tree:
            zwróć self.compile_node(root), root
        inaczej:
            zwróć self.compile_node(root)

    def compile_node(self, node):
        """Compiles a node, recursively.

        This jest one big switch on the node type.
        """
        # XXX Optimize certain Wildcard-containing-Wildcard patterns
        # that can be merged
        jeżeli node.type == self.syms.Matcher:
            node = node.children[0] # Avoid unneeded recursion

        jeżeli node.type == self.syms.Alternatives:
            # Skip the odd children since they are just '|' tokens
            alts = [self.compile_node(ch) dla ch w node.children[::2]]
            jeżeli len(alts) == 1:
                zwróć alts[0]
            p = pytree.WildcardPattern([[a] dla a w alts], min=1, max=1)
            zwróć p.optimize()

        jeżeli node.type == self.syms.Alternative:
            units = [self.compile_node(ch) dla ch w node.children]
            jeżeli len(units) == 1:
                zwróć units[0]
            p = pytree.WildcardPattern([units], min=1, max=1)
            zwróć p.optimize()

        jeżeli node.type == self.syms.NegatedUnit:
            pattern = self.compile_basic(node.children[1:])
            p = pytree.NegatedPattern(pattern)
            zwróć p.optimize()

        assert node.type == self.syms.Unit

        name = Nic
        nodes = node.children
        jeżeli len(nodes) >= 3 oraz nodes[1].type == token.EQUAL:
            name = nodes[0].value
            nodes = nodes[2:]
        repeat = Nic
        jeżeli len(nodes) >= 2 oraz nodes[-1].type == self.syms.Repeater:
            repeat = nodes[-1]
            nodes = nodes[:-1]

        # Now we've reduced it to: STRING | NAME [Details] | (...) | [...]
        pattern = self.compile_basic(nodes, repeat)

        jeżeli repeat jest nie Nic:
            assert repeat.type == self.syms.Repeater
            children = repeat.children
            child = children[0]
            jeżeli child.type == token.STAR:
                min = 0
                max = pytree.HUGE
            albo_inaczej child.type == token.PLUS:
                min = 1
                max = pytree.HUGE
            albo_inaczej child.type == token.LBRACE:
                assert children[-1].type == token.RBRACE
                assert  len(children) w (3, 5)
                min = max = self.get_int(children[1])
                jeżeli len(children) == 5:
                    max = self.get_int(children[3])
            inaczej:
                assert Nieprawda
            jeżeli min != 1 albo max != 1:
                pattern = pattern.optimize()
                pattern = pytree.WildcardPattern([[pattern]], min=min, max=max)

        jeżeli name jest nie Nic:
            pattern.name = name
        zwróć pattern.optimize()

    def compile_basic(self, nodes, repeat=Nic):
        # Compile STRING | NAME [Details] | (...) | [...]
        assert len(nodes) >= 1
        node = nodes[0]
        jeżeli node.type == token.STRING:
            value = str(literals.evalString(node.value))
            zwróć pytree.LeafPattern(_type_of_literal(value), value)
        albo_inaczej node.type == token.NAME:
            value = node.value
            jeżeli value.isupper():
                jeżeli value nie w TOKEN_MAP:
                    podnieś PatternSyntaxError("Invalid token: %r" % value)
                jeżeli nodes[1:]:
                    podnieś PatternSyntaxError("Can't have details dla token")
                zwróć pytree.LeafPattern(TOKEN_MAP[value])
            inaczej:
                jeżeli value == "any":
                    type = Nic
                albo_inaczej nie value.startswith("_"):
                    type = getattr(self.pysyms, value, Nic)
                    jeżeli type jest Nic:
                        podnieś PatternSyntaxError("Invalid symbol: %r" % value)
                jeżeli nodes[1:]: # Details present
                    content = [self.compile_node(nodes[1].children[1])]
                inaczej:
                    content = Nic
                zwróć pytree.NodePattern(type, content)
        albo_inaczej node.value == "(":
            zwróć self.compile_node(nodes[1])
        albo_inaczej node.value == "[":
            assert repeat jest Nic
            subpattern = self.compile_node(nodes[1])
            zwróć pytree.WildcardPattern([[subpattern]], min=0, max=1)
        assert Nieprawda, node

    def get_int(self, node):
        assert node.type == token.NUMBER
        zwróć int(node.value)


# Map named tokens to the type value dla a LeafPattern
TOKEN_MAP = {"NAME": token.NAME,
             "STRING": token.STRING,
             "NUMBER": token.NUMBER,
             "TOKEN": Nic}


def _type_of_literal(value):
    jeżeli value[0].isalpha():
        zwróć token.NAME
    albo_inaczej value w grammar.opmap:
        zwróć grammar.opmap[value]
    inaczej:
        zwróć Nic


def pattern_convert(grammar, raw_node_info):
    """Converts raw node information to a Node albo Leaf instance."""
    type, value, context, children = raw_node_info
    jeżeli children albo type w grammar.number2symbol:
        zwróć pytree.Node(type, children, context=context)
    inaczej:
        zwróć pytree.Leaf(type, value, context=context)


def compile_pattern(pattern):
    zwróć PatternCompiler().compile_pattern(pattern)
