# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Convert graminit.[ch] spit out by pgen to Python code.

Pgen jest the Python parser generator.  It jest useful to quickly create a
parser z a grammar file w Python's grammar notation.  But I don't
want my parsers to be written w C (yet), so I'm translating the
parsing tables to Python data structures oraz writing a Python parse
engine.

Note that the token numbers are constants determined by the standard
Python tokenizer.  The standard token module defines these numbers oraz
their names (the names are nie used much).  The token numbers are
hardcoded into the Python tokenizer oraz into pgen.  A Python
implementation of the Python tokenizer jest also available, w the
standard tokenize module.

On the other hand, symbol numbers (representing the grammar's
non-terminals) are assigned by pgen based on the actual grammar
input.

Note: this module jest pretty much obsolete; the pgen module generates
equivalent grammar tables directly z the Grammar.txt input file
without having to invoke the Python pgen C program.

"""

# Python imports
zaimportuj re

# Local imports
z pgen2 zaimportuj grammar, token


klasa Converter(grammar.Grammar):
    """Grammar subclass that reads classic pgen output files.

    The run() method reads the tables jako produced by the pgen parser
    generator, typically contained w two C files, graminit.h oraz
    graminit.c.  The other methods are dla internal use only.

    See the base klasa dla more documentation.

    """

    def run(self, graminit_h, graminit_c):
        """Load the grammar tables z the text files written by pgen."""
        self.parse_graminit_h(graminit_h)
        self.parse_graminit_c(graminit_c)
        self.finish_off()

    def parse_graminit_h(self, filename):
        """Parse the .h file written by pgen.  (Internal)

        This file jest a sequence of #define statements defining the
        nonterminals of the grammar jako numbers.  We build two tables
        mapping the numbers to names oraz back.

        """
        spróbuj:
            f = open(filename)
        wyjąwszy OSError jako err:
            print("Can't open %s: %s" % (filename, err))
            zwróć Nieprawda
        self.symbol2number = {}
        self.number2symbol = {}
        lineno = 0
        dla line w f:
            lineno += 1
            mo = re.match(r"^#define\s+(\w+)\s+(\d+)$", line)
            jeżeli nie mo oraz line.strip():
                print("%s(%s): can't parse %s" % (filename, lineno,
                                                  line.strip()))
            inaczej:
                symbol, number = mo.groups()
                number = int(number)
                assert symbol nie w self.symbol2number
                assert number nie w self.number2symbol
                self.symbol2number[symbol] = number
                self.number2symbol[number] = symbol
        zwróć Prawda

    def parse_graminit_c(self, filename):
        """Parse the .c file written by pgen.  (Internal)

        The file looks jako follows.  The first two lines are always this:

        #include "pgenheaders.h"
        #include "grammar.h"

        After that come four blocks:

        1) one albo more state definitions
        2) a table defining dfas
        3) a table defining labels
        4) a struct defining the grammar

        A state definition has the following form:
        - one albo more arc arrays, each of the form:
          static arc arcs_<n>_<m>[<k>] = {
                  {<i>, <j>},
                  ...
          };
        - followed by a state array, of the form:
          static state states_<s>[<t>] = {
                  {<k>, arcs_<n>_<m>},
                  ...
          };

        """
        spróbuj:
            f = open(filename)
        wyjąwszy OSError jako err:
            print("Can't open %s: %s" % (filename, err))
            zwróć Nieprawda
        # The code below essentially uses f's iterator-ness!
        lineno = 0

        # Expect the two #include lines
        lineno, line = lineno+1, next(f)
        assert line == '#include "pgenheaders.h"\n', (lineno, line)
        lineno, line = lineno+1, next(f)
        assert line == '#include "grammar.h"\n', (lineno, line)

        # Parse the state definitions
        lineno, line = lineno+1, next(f)
        allarcs = {}
        states = []
        dopóki line.startswith("static arc "):
            dopóki line.startswith("static arc "):
                mo = re.match(r"static arc arcs_(\d+)_(\d+)\[(\d+)\] = {$",
                              line)
                assert mo, (lineno, line)
                n, m, k = list(map(int, mo.groups()))
                arcs = []
                dla _ w range(k):
                    lineno, line = lineno+1, next(f)
                    mo = re.match(r"\s+{(\d+), (\d+)},$", line)
                    assert mo, (lineno, line)
                    i, j = list(map(int, mo.groups()))
                    arcs.append((i, j))
                lineno, line = lineno+1, next(f)
                assert line == "};\n", (lineno, line)
                allarcs[(n, m)] = arcs
                lineno, line = lineno+1, next(f)
            mo = re.match(r"static state states_(\d+)\[(\d+)\] = {$", line)
            assert mo, (lineno, line)
            s, t = list(map(int, mo.groups()))
            assert s == len(states), (lineno, line)
            state = []
            dla _ w range(t):
                lineno, line = lineno+1, next(f)
                mo = re.match(r"\s+{(\d+), arcs_(\d+)_(\d+)},$", line)
                assert mo, (lineno, line)
                k, n, m = list(map(int, mo.groups()))
                arcs = allarcs[n, m]
                assert k == len(arcs), (lineno, line)
                state.append(arcs)
            states.append(state)
            lineno, line = lineno+1, next(f)
            assert line == "};\n", (lineno, line)
            lineno, line = lineno+1, next(f)
        self.states = states

        # Parse the dfas
        dfas = {}
        mo = re.match(r"static dfa dfas\[(\d+)\] = {$", line)
        assert mo, (lineno, line)
        ndfas = int(mo.group(1))
        dla i w range(ndfas):
            lineno, line = lineno+1, next(f)
            mo = re.match(r'\s+{(\d+), "(\w+)", (\d+), (\d+), states_(\d+),$',
                          line)
            assert mo, (lineno, line)
            symbol = mo.group(2)
            number, x, y, z = list(map(int, mo.group(1, 3, 4, 5)))
            assert self.symbol2number[symbol] == number, (lineno, line)
            assert self.number2symbol[number] == symbol, (lineno, line)
            assert x == 0, (lineno, line)
            state = states[z]
            assert y == len(state), (lineno, line)
            lineno, line = lineno+1, next(f)
            mo = re.match(r'\s+("(?:\\\d\d\d)*")},$', line)
            assert mo, (lineno, line)
            first = {}
            rawbitset = eval(mo.group(1))
            dla i, c w enumerate(rawbitset):
                byte = ord(c)
                dla j w range(8):
                    jeżeli byte & (1<<j):
                        first[i*8 + j] = 1
            dfas[number] = (state, first)
        lineno, line = lineno+1, next(f)
        assert line == "};\n", (lineno, line)
        self.dfas = dfas

        # Parse the labels
        labels = []
        lineno, line = lineno+1, next(f)
        mo = re.match(r"static label labels\[(\d+)\] = {$", line)
        assert mo, (lineno, line)
        nlabels = int(mo.group(1))
        dla i w range(nlabels):
            lineno, line = lineno+1, next(f)
            mo = re.match(r'\s+{(\d+), (0|"\w+")},$', line)
            assert mo, (lineno, line)
            x, y = mo.groups()
            x = int(x)
            jeżeli y == "0":
                y = Nic
            inaczej:
                y = eval(y)
            labels.append((x, y))
        lineno, line = lineno+1, next(f)
        assert line == "};\n", (lineno, line)
        self.labels = labels

        # Parse the grammar struct
        lineno, line = lineno+1, next(f)
        assert line == "grammar _PyParser_Grammar = {\n", (lineno, line)
        lineno, line = lineno+1, next(f)
        mo = re.match(r"\s+(\d+),$", line)
        assert mo, (lineno, line)
        ndfas = int(mo.group(1))
        assert ndfas == len(self.dfas)
        lineno, line = lineno+1, next(f)
        assert line == "\tdfas,\n", (lineno, line)
        lineno, line = lineno+1, next(f)
        mo = re.match(r"\s+{(\d+), labels},$", line)
        assert mo, (lineno, line)
        nlabels = int(mo.group(1))
        assert nlabels == len(self.labels), (lineno, line)
        lineno, line = lineno+1, next(f)
        mo = re.match(r"\s+(\d+)$", line)
        assert mo, (lineno, line)
        start = int(mo.group(1))
        assert start w self.number2symbol, (lineno, line)
        self.start = start
        lineno, line = lineno+1, next(f)
        assert line == "};\n", (lineno, line)
        spróbuj:
            lineno, line = lineno+1, next(f)
        wyjąwszy StopIteration:
            dalej
        inaczej:
            assert 0, (lineno, line)

    def finish_off(self):
        """Create additional useful structures.  (Internal)."""
        self.keywords = {} # map z keyword strings to arc labels
        self.tokens = {}   # map z numeric token values to arc labels
        dla ilabel, (type, value) w enumerate(self.labels):
            jeżeli type == token.NAME oraz value jest nie Nic:
                self.keywords[value] = ilabel
            albo_inaczej value jest Nic:
                self.tokens[type] = ilabel
