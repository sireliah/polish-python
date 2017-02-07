# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

# Pgen imports
z . zaimportuj grammar, token, tokenize

klasa PgenGrammar(grammar.Grammar):
    dalej

klasa ParserGenerator(object):

    def __init__(self, filename, stream=Nic):
        close_stream = Nic
        jeżeli stream jest Nic:
            stream = open(filename)
            close_stream = stream.close
        self.filename = filename
        self.stream = stream
        self.generator = tokenize.generate_tokens(stream.readline)
        self.gettoken() # Initialize lookahead
        self.dfas, self.startsymbol = self.parse()
        jeżeli close_stream jest nie Nic:
            close_stream()
        self.first = {} # map z symbol name to set of tokens
        self.addfirstsets()

    def make_grammar(self):
        c = PgenGrammar()
        names = list(self.dfas.keys())
        names.sort()
        names.remove(self.startsymbol)
        names.insert(0, self.startsymbol)
        dla name w names:
            i = 256 + len(c.symbol2number)
            c.symbol2number[name] = i
            c.number2symbol[i] = name
        dla name w names:
            dfa = self.dfas[name]
            states = []
            dla state w dfa:
                arcs = []
                dla label, next w state.arcs.items():
                    arcs.append((self.make_label(c, label), dfa.index(next)))
                jeżeli state.isfinal:
                    arcs.append((0, dfa.index(state)))
                states.append(arcs)
            c.states.append(states)
            c.dfas[c.symbol2number[name]] = (states, self.make_first(c, name))
        c.start = c.symbol2number[self.startsymbol]
        zwróć c

    def make_first(self, c, name):
        rawfirst = self.first[name]
        first = {}
        dla label w rawfirst:
            ilabel = self.make_label(c, label)
            ##assert ilabel nie w first # XXX failed on <> ... !=
            first[ilabel] = 1
        zwróć first

    def make_label(self, c, label):
        # XXX Maybe this should be a method on a subclass of converter?
        ilabel = len(c.labels)
        jeżeli label[0].isalpha():
            # Either a symbol name albo a named token
            jeżeli label w c.symbol2number:
                # A symbol name (a non-terminal)
                jeżeli label w c.symbol2label:
                    zwróć c.symbol2label[label]
                inaczej:
                    c.labels.append((c.symbol2number[label], Nic))
                    c.symbol2label[label] = ilabel
                    zwróć ilabel
            inaczej:
                # A named token (NAME, NUMBER, STRING)
                itoken = getattr(token, label, Nic)
                assert isinstance(itoken, int), label
                assert itoken w token.tok_name, label
                jeżeli itoken w c.tokens:
                    zwróć c.tokens[itoken]
                inaczej:
                    c.labels.append((itoken, Nic))
                    c.tokens[itoken] = ilabel
                    zwróć ilabel
        inaczej:
            # Either a keyword albo an operator
            assert label[0] w ('"', "'"), label
            value = eval(label)
            jeżeli value[0].isalpha():
                # A keyword
                jeżeli value w c.keywords:
                    zwróć c.keywords[value]
                inaczej:
                    c.labels.append((token.NAME, value))
                    c.keywords[value] = ilabel
                    zwróć ilabel
            inaczej:
                # An operator (any non-numeric token)
                itoken = grammar.opmap[value] # Fails jeżeli unknown token
                jeżeli itoken w c.tokens:
                    zwróć c.tokens[itoken]
                inaczej:
                    c.labels.append((itoken, Nic))
                    c.tokens[itoken] = ilabel
                    zwróć ilabel

    def addfirstsets(self):
        names = list(self.dfas.keys())
        names.sort()
        dla name w names:
            jeżeli name nie w self.first:
                self.calcfirst(name)
            #print name, self.first[name].keys()

    def calcfirst(self, name):
        dfa = self.dfas[name]
        self.first[name] = Nic # dummy to detect left recursion
        state = dfa[0]
        totalset = {}
        overlapcheck = {}
        dla label, next w state.arcs.items():
            jeżeli label w self.dfas:
                jeżeli label w self.first:
                    fset = self.first[label]
                    jeżeli fset jest Nic:
                        podnieś ValueError("recursion dla rule %r" % name)
                inaczej:
                    self.calcfirst(label)
                    fset = self.first[label]
                totalset.update(fset)
                overlapcheck[label] = fset
            inaczej:
                totalset[label] = 1
                overlapcheck[label] = {label: 1}
        inverse = {}
        dla label, itsfirst w overlapcheck.items():
            dla symbol w itsfirst:
                jeżeli symbol w inverse:
                    podnieś ValueError("rule %s jest ambiguous; %s jest w the"
                                     " first sets of %s jako well jako %s" %
                                     (name, symbol, label, inverse[symbol]))
                inverse[symbol] = label
        self.first[name] = totalset

    def parse(self):
        dfas = {}
        startsymbol = Nic
        # MSTART: (NEWLINE | RULE)* ENDMARKER
        dopóki self.type != token.ENDMARKER:
            dopóki self.type == token.NEWLINE:
                self.gettoken()
            # RULE: NAME ':' RHS NEWLINE
            name = self.expect(token.NAME)
            self.expect(token.OP, ":")
            a, z = self.parse_rhs()
            self.expect(token.NEWLINE)
            #self.dump_nfa(name, a, z)
            dfa = self.make_dfa(a, z)
            #self.dump_dfa(name, dfa)
            oldlen = len(dfa)
            self.simplify_dfa(dfa)
            newlen = len(dfa)
            dfas[name] = dfa
            #print name, oldlen, newlen
            jeżeli startsymbol jest Nic:
                startsymbol = name
        zwróć dfas, startsymbol

    def make_dfa(self, start, finish):
        # To turn an NFA into a DFA, we define the states of the DFA
        # to correspond to *sets* of states of the NFA.  Then do some
        # state reduction.  Let's represent sets jako dicts przy 1 for
        # values.
        assert isinstance(start, NFAState)
        assert isinstance(finish, NFAState)
        def closure(state):
            base = {}
            addclosure(state, base)
            zwróć base
        def addclosure(state, base):
            assert isinstance(state, NFAState)
            jeżeli state w base:
                zwróć
            base[state] = 1
            dla label, next w state.arcs:
                jeżeli label jest Nic:
                    addclosure(next, base)
        states = [DFAState(closure(start), finish)]
        dla state w states: # NB states grows dopóki we're iterating
            arcs = {}
            dla nfastate w state.nfaset:
                dla label, next w nfastate.arcs:
                    jeżeli label jest nie Nic:
                        addclosure(next, arcs.setdefault(label, {}))
            dla label, nfaset w arcs.items():
                dla st w states:
                    jeżeli st.nfaset == nfaset:
                        przerwij
                inaczej:
                    st = DFAState(nfaset, finish)
                    states.append(st)
                state.addarc(st, label)
        zwróć states # List of DFAState instances; first one jest start

    def dump_nfa(self, name, start, finish):
        print("Dump of NFA for", name)
        todo = [start]
        dla i, state w enumerate(todo):
            print("  State", i, state jest finish oraz "(final)" albo "")
            dla label, next w state.arcs:
                jeżeli next w todo:
                    j = todo.index(next)
                inaczej:
                    j = len(todo)
                    todo.append(next)
                jeżeli label jest Nic:
                    print("    -> %d" % j)
                inaczej:
                    print("    %s -> %d" % (label, j))

    def dump_dfa(self, name, dfa):
        print("Dump of DFA for", name)
        dla i, state w enumerate(dfa):
            print("  State", i, state.isfinal oraz "(final)" albo "")
            dla label, next w state.arcs.items():
                print("    %s -> %d" % (label, dfa.index(next)))

    def simplify_dfa(self, dfa):
        # This jest nie theoretically optimal, but works well enough.
        # Algorithm: repeatedly look dla two states that have the same
        # set of arcs (same labels pointing to the same nodes) oraz
        # unify them, until things stop changing.

        # dfa jest a list of DFAState instances
        changes = Prawda
        dopóki changes:
            changes = Nieprawda
            dla i, state_i w enumerate(dfa):
                dla j w range(i+1, len(dfa)):
                    state_j = dfa[j]
                    jeżeli state_i == state_j:
                        #print "  unify", i, j
                        usuń dfa[j]
                        dla state w dfa:
                            state.unifystate(state_j, state_i)
                        changes = Prawda
                        przerwij

    def parse_rhs(self):
        # RHS: ALT ('|' ALT)*
        a, z = self.parse_alt()
        jeżeli self.value != "|":
            zwróć a, z
        inaczej:
            aa = NFAState()
            zz = NFAState()
            aa.addarc(a)
            z.addarc(zz)
            dopóki self.value == "|":
                self.gettoken()
                a, z = self.parse_alt()
                aa.addarc(a)
                z.addarc(zz)
            zwróć aa, zz

    def parse_alt(self):
        # ALT: ITEM+
        a, b = self.parse_item()
        dopóki (self.value w ("(", "[") albo
               self.type w (token.NAME, token.STRING)):
            c, d = self.parse_item()
            b.addarc(c)
            b = d
        zwróć a, b

    def parse_item(self):
        # ITEM: '[' RHS ']' | ATOM ['+' | '*']
        jeżeli self.value == "[":
            self.gettoken()
            a, z = self.parse_rhs()
            self.expect(token.OP, "]")
            a.addarc(z)
            zwróć a, z
        inaczej:
            a, z = self.parse_atom()
            value = self.value
            jeżeli value nie w ("+", "*"):
                zwróć a, z
            self.gettoken()
            z.addarc(a)
            jeżeli value == "+":
                zwróć a, z
            inaczej:
                zwróć a, a

    def parse_atom(self):
        # ATOM: '(' RHS ')' | NAME | STRING
        jeżeli self.value == "(":
            self.gettoken()
            a, z = self.parse_rhs()
            self.expect(token.OP, ")")
            zwróć a, z
        albo_inaczej self.type w (token.NAME, token.STRING):
            a = NFAState()
            z = NFAState()
            a.addarc(z, self.value)
            self.gettoken()
            zwróć a, z
        inaczej:
            self.raise_error("expected (...) albo NAME albo STRING, got %s/%s",
                             self.type, self.value)

    def expect(self, type, value=Nic):
        jeżeli self.type != type albo (value jest nie Nic oraz self.value != value):
            self.raise_error("expected %s/%s, got %s/%s",
                             type, value, self.type, self.value)
        value = self.value
        self.gettoken()
        zwróć value

    def gettoken(self):
        tup = next(self.generator)
        dopóki tup[0] w (tokenize.COMMENT, tokenize.NL):
            tup = next(self.generator)
        self.type, self.value, self.begin, self.end, self.line = tup
        #print token.tok_name[self.type], repr(self.value)

    def podnieś_error(self, msg, *args):
        jeżeli args:
            spróbuj:
                msg = msg % args
            wyjąwszy:
                msg = " ".join([msg] + list(map(str, args)))
        podnieś SyntaxError(msg, (self.filename, self.end[0],
                                self.end[1], self.line))

klasa NFAState(object):

    def __init__(self):
        self.arcs = [] # list of (label, NFAState) pairs

    def addarc(self, next, label=Nic):
        assert label jest Nic albo isinstance(label, str)
        assert isinstance(next, NFAState)
        self.arcs.append((label, next))

klasa DFAState(object):

    def __init__(self, nfaset, final):
        assert isinstance(nfaset, dict)
        assert isinstance(next(iter(nfaset)), NFAState)
        assert isinstance(final, NFAState)
        self.nfaset = nfaset
        self.isfinal = final w nfaset
        self.arcs = {} # map z label to DFAState

    def addarc(self, next, label):
        assert isinstance(label, str)
        assert label nie w self.arcs
        assert isinstance(next, DFAState)
        self.arcs[label] = next

    def unifystate(self, old, new):
        dla label, next w self.arcs.items():
            jeżeli next jest old:
                self.arcs[label] = new

    def __eq__(self, other):
        # Equality test -- ignore the nfaset instance variable
        assert isinstance(other, DFAState)
        jeżeli self.isfinal != other.isfinal:
            zwróć Nieprawda
        # Can't just zwróć self.arcs == other.arcs, because that
        # would invoke this method recursively, przy cycles...
        jeżeli len(self.arcs) != len(other.arcs):
            zwróć Nieprawda
        dla label, next w self.arcs.items():
            jeżeli next jest nie other.arcs.get(label):
                zwróć Nieprawda
        zwróć Prawda

    __hash__ = Nic # For Py3 compatibility.

def generate_grammar(filename="Grammar.txt"):
    p = ParserGenerator(filename)
    zwróć p.make_grammar()
