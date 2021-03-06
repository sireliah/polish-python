# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Parser engine dla the grammar tables generated by pgen.

The grammar table must be loaded first.

See Parser/parser.c w the Python distribution dla additional info on
how this parsing engine works.

"""

# Local imports
z . zaimportuj token

klasa ParseError(Exception):
    """Exception to signal the parser jest stuck."""

    def __init__(self, msg, type, value, context):
        Exception.__init__(self, "%s: type=%r, value=%r, context=%r" %
                           (msg, type, value, context))
        self.msg = msg
        self.type = type
        self.value = value
        self.context = context

klasa Parser(object):
    """Parser engine.

    The proper usage sequence is:

    p = Parser(grammar, [converter])  # create instance
    p.setup([start])                  # prepare dla parsing
    <dla each input token>:
        jeżeli p.addtoken(...):           # parse a token; may podnieś ParseError
            przerwij
    root = p.rootnode                 # root of abstract syntax tree

    A Parser instance may be reused by calling setup() repeatedly.

    A Parser instance contains state pertaining to the current token
    sequence, oraz should nie be used concurrently by different threads
    to parse separate token sequences.

    See driver.py dla how to get input tokens by tokenizing a file albo
    string.

    Parsing jest complete when addtoken() returns Prawda; the root of the
    abstract syntax tree can then be retrieved z the rootnode
    instance variable.  When a syntax error occurs, addtoken() podnieśs
    the ParseError exception.  There jest no error recovery; the parser
    cannot be used after a syntax error was reported (but it can be
    reinitialized by calling setup()).

    """

    def __init__(self, grammar, convert=Nic):
        """Constructor.

        The grammar argument jest a grammar.Grammar instance; see the
        grammar module dla more information.

        The parser jest nie ready yet dla parsing; you must call the
        setup() method to get it started.

        The optional convert argument jest a function mapping concrete
        syntax tree nodes to abstract syntax tree nodes.  If nie
        given, no conversion jest done oraz the syntax tree produced jest
        the concrete syntax tree.  If given, it must be a function of
        two arguments, the first being the grammar (a grammar.Grammar
        instance), oraz the second being the concrete syntax tree node
        to be converted.  The syntax tree jest converted z the bottom
        up.

        A concrete syntax tree node jest a (type, value, context, nodes)
        tuple, where type jest the node type (a token albo symbol number),
        value jest Nic dla symbols oraz a string dla tokens, context jest
        Nic albo an opaque value used dla error reporting (typically a
        (lineno, offset) pair), oraz nodes jest a list of children for
        symbols, oraz Nic dla tokens.

        An abstract syntax tree node may be anything; this jest entirely
        up to the converter function.

        """
        self.grammar = grammar
        self.convert = convert albo (lambda grammar, node: node)

    def setup(self, start=Nic):
        """Prepare dla parsing.

        This *must* be called before starting to parse.

        The optional argument jest an alternative start symbol; it
        defaults to the grammar's start symbol.

        You can use a Parser instance to parse any number of programs;
        each time you call setup() the parser jest reset to an initial
        state determined by the (implicit albo explicit) start symbol.

        """
        jeżeli start jest Nic:
            start = self.grammar.start
        # Each stack entry jest a tuple: (dfa, state, node).
        # A node jest a tuple: (type, value, context, children),
        # where children jest a list of nodes albo Nic, oraz context may be Nic.
        newnode = (start, Nic, Nic, [])
        stackentry = (self.grammar.dfas[start], 0, newnode)
        self.stack = [stackentry]
        self.rootnode = Nic
        self.used_names = set() # Aliased to self.rootnode.used_names w pop()

    def addtoken(self, type, value, context):
        """Add a token; zwróć Prawda iff this jest the end of the program."""
        # Map z token to label
        ilabel = self.classify(type, value, context)
        # Loop until the token jest shifted; may podnieś exceptions
        dopóki Prawda:
            dfa, state, node = self.stack[-1]
            states, first = dfa
            arcs = states[state]
            # Look dla a state przy this label
            dla i, newstate w arcs:
                t, v = self.grammar.labels[i]
                jeżeli ilabel == i:
                    # Look it up w the list of labels
                    assert t < 256
                    # Shift a token; we're done przy it
                    self.shift(type, value, newstate, context)
                    # Pop dopóki we are w an accept-only state
                    state = newstate
                    dopóki states[state] == [(0, state)]:
                        self.pop()
                        jeżeli nie self.stack:
                            # Done parsing!
                            zwróć Prawda
                        dfa, state, node = self.stack[-1]
                        states, first = dfa
                    # Done przy this token
                    zwróć Nieprawda
                albo_inaczej t >= 256:
                    # See jeżeli it's a symbol oraz jeżeli we're w its first set
                    itsdfa = self.grammar.dfas[t]
                    itsstates, itsfirst = itsdfa
                    jeżeli ilabel w itsfirst:
                        # Push a symbol
                        self.push(t, self.grammar.dfas[t], newstate, context)
                        przerwij # To continue the outer dopóki loop
            inaczej:
                jeżeli (0, state) w arcs:
                    # An accepting state, pop it oraz try something inaczej
                    self.pop()
                    jeżeli nie self.stack:
                        # Done parsing, but another token jest input
                        podnieś ParseError("too much input",
                                         type, value, context)
                inaczej:
                    # No success finding a transition
                    podnieś ParseError("bad input", type, value, context)

    def classify(self, type, value, context):
        """Turn a token into a label.  (Internal)"""
        jeżeli type == token.NAME:
            # Keep a listing of all used names
            self.used_names.add(value)
            # Check dla reserved words
            ilabel = self.grammar.keywords.get(value)
            jeżeli ilabel jest nie Nic:
                zwróć ilabel
        ilabel = self.grammar.tokens.get(type)
        jeżeli ilabel jest Nic:
            podnieś ParseError("bad token", type, value, context)
        zwróć ilabel

    def shift(self, type, value, newstate, context):
        """Shift a token.  (Internal)"""
        dfa, state, node = self.stack[-1]
        newnode = (type, value, context, Nic)
        newnode = self.convert(self.grammar, newnode)
        jeżeli newnode jest nie Nic:
            node[-1].append(newnode)
        self.stack[-1] = (dfa, newstate, node)

    def push(self, type, newdfa, newstate, context):
        """Push a nonterminal.  (Internal)"""
        dfa, state, node = self.stack[-1]
        newnode = (type, Nic, context, [])
        self.stack[-1] = (dfa, newstate, node)
        self.stack.append((newdfa, 0, newnode))

    def pop(self):
        """Pop a nonterminal.  (Internal)"""
        popdfa, popstate, popnode = self.stack.pop()
        newnode = self.convert(self.grammar, popnode)
        jeżeli newnode jest nie Nic:
            jeżeli self.stack:
                dfa, state, node = self.stack[-1]
                node[-1].append(newnode)
            inaczej:
                self.rootnode = newnode
                self.rootnode.used_names = self.used_names
