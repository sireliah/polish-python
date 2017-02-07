# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""This module defines the data structures used to represent a grammar.

These are a bit arcane because they are derived z the data
structures used by Python's 'pgen' parser generator.

There's also a table here mapping operators to their names w the
token module; the Python tokenize module reports all operators jako the
fallback token code OP, but the parser needs the actual token code.

"""

# Python imports
zaimportuj pickle

# Local imports
z . zaimportuj token, tokenize


klasa Grammar(object):
    """Pgen parsing tables conversion class.

    Once initialized, this klasa supplies the grammar tables dla the
    parsing engine implemented by parse.py.  The parsing engine
    accesses the instance variables directly.  The klasa here does nie
    provide initialization of the tables; several subclasses exist to
    do this (see the conv oraz pgen modules).

    The load() method reads the tables z a pickle file, which jest
    much faster than the other ways offered by subclasses.  The pickle
    file jest written by calling dump() (after loading the grammar
    tables using a subclass).  The report() method prints a readable
    representation of the tables to stdout, dla debugging.

    The instance variables are jako follows:

    symbol2number -- a dict mapping symbol names to numbers.  Symbol
                     numbers are always 256 albo higher, to distinguish
                     them z token numbers, which are between 0 oraz
                     255 (inclusive).

    number2symbol -- a dict mapping numbers to symbol names;
                     these two are each other's inverse.

    states        -- a list of DFAs, where each DFA jest a list of
                     states, each state jest a list of arcs, oraz each
                     arc jest a (i, j) pair where i jest a label oraz j jest
                     a state number.  The DFA number jest the index into
                     this list.  (This name jest slightly confusing.)
                     Final states are represented by a special arc of
                     the form (0, j) where j jest its own state number.

    dfas          -- a dict mapping symbol numbers to (DFA, first)
                     pairs, where DFA jest an item z the states list
                     above, oraz first jest a set of tokens that can
                     begin this grammar rule (represented by a dict
                     whose values are always 1).

    labels        -- a list of (x, y) pairs where x jest either a token
                     number albo a symbol number, oraz y jest either Nic
                     albo a string; the strings are keywords.  The label
                     number jest the index w this list; label numbers
                     are used to mark state transitions (arcs) w the
                     DFAs.

    start         -- the number of the grammar's start symbol.

    keywords      -- a dict mapping keyword strings to arc labels.

    tokens        -- a dict mapping token numbers to arc labels.

    """

    def __init__(self):
        self.symbol2number = {}
        self.number2symbol = {}
        self.states = []
        self.dfas = {}
        self.labels = [(0, "EMPTY")]
        self.keywords = {}
        self.tokens = {}
        self.symbol2label = {}
        self.start = 256

    def dump(self, filename):
        """Dump the grammar tables to a pickle file."""
        przy open(filename, "wb") jako f:
            pickle.dump(self.__dict__, f, 2)

    def load(self, filename):
        """Load the grammar tables z a pickle file."""
        przy open(filename, "rb") jako f:
            d = pickle.load(f)
        self.__dict__.update(d)

    def copy(self):
        """
        Copy the grammar.
        """
        new = self.__class__()
        dla dict_attr w ("symbol2number", "number2symbol", "dfas", "keywords",
                          "tokens", "symbol2label"):
            setattr(new, dict_attr, getattr(self, dict_attr).copy())
        new.labels = self.labels[:]
        new.states = self.states[:]
        new.start = self.start
        zwróć new

    def report(self):
        """Dump the grammar tables to standard output, dla debugging."""
        z pprint zaimportuj pprint
        print("s2n")
        pprint(self.symbol2number)
        print("n2s")
        pprint(self.number2symbol)
        print("states")
        pprint(self.states)
        print("dfas")
        pprint(self.dfas)
        print("labels")
        pprint(self.labels)
        print("start", self.start)


# Map z operator to number (since tokenize doesn't do this)

opmap_raw = """
( LPAR
) RPAR
[ LSQB
] RSQB
: COLON
, COMMA
; SEMI
+ PLUS
- MINUS
* STAR
/ SLASH
| VBAR
& AMPER
< LESS
> GREATER
= EQUAL
. DOT
% PERCENT
` BACKQUOTE
{ LBRACE
} RBRACE
@ AT
@= ATEQUAL
== EQEQUAL
!= NOTEQUAL
<> NOTEQUAL
<= LESSEQUAL
>= GREATEREQUAL
~ TILDE
^ CIRCUMFLEX
<< LEFTSHIFT
>> RIGHTSHIFT
** DOUBLESTAR
+= PLUSEQUAL
-= MINEQUAL
*= STAREQUAL
/= SLASHEQUAL
%= PERCENTEQUAL
&= AMPEREQUAL
|= VBAREQUAL
^= CIRCUMFLEXEQUAL
<<= LEFTSHIFTEQUAL
>>= RIGHTSHIFTEQUAL
**= DOUBLESTAREQUAL
// DOUBLESLASH
//= DOUBLESLASHEQUAL
-> RARROW
"""

opmap = {}
dla line w opmap_raw.splitlines():
    jeżeli line:
        op, name = line.split()
        opmap[op] = getattr(token, name)
