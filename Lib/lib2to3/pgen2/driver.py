# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

# Modifications:
# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Parser driver.

This provides a high-level interface to parse a file into a syntax tree.

"""

__author__ = "Guido van Rossum <guido@python.org>"

__all__ = ["Driver", "load_grammar"]

# Python imports
zaimportuj codecs
zaimportuj io
zaimportuj os
zaimportuj logging
zaimportuj sys

# Pgen imports
z . zaimportuj grammar, parse, token, tokenize, pgen


klasa Driver(object):

    def __init__(self, grammar, convert=Nic, logger=Nic):
        self.grammar = grammar
        jeżeli logger jest Nic:
            logger = logging.getLogger()
        self.logger = logger
        self.convert = convert

    def parse_tokens(self, tokens, debug=Nieprawda):
        """Parse a series of tokens oraz zwróć the syntax tree."""
        # XXX Move the prefix computation into a wrapper around tokenize.
        p = parse.Parser(self.grammar, self.convert)
        p.setup()
        lineno = 1
        column = 0
        type = value = start = end = line_text = Nic
        prefix = ""
        dla quintuple w tokens:
            type, value, start, end, line_text = quintuple
            jeżeli start != (lineno, column):
                assert (lineno, column) <= start, ((lineno, column), start)
                s_lineno, s_column = start
                jeżeli lineno < s_lineno:
                    prefix += "\n" * (s_lineno - lineno)
                    lineno = s_lineno
                    column = 0
                jeżeli column < s_column:
                    prefix += line_text[column:s_column]
                    column = s_column
            jeżeli type w (tokenize.COMMENT, tokenize.NL):
                prefix += value
                lineno, column = end
                jeżeli value.endswith("\n"):
                    lineno += 1
                    column = 0
                kontynuuj
            jeżeli type == token.OP:
                type = grammar.opmap[value]
            jeżeli debug:
                self.logger.debug("%s %r (prefix=%r)",
                                  token.tok_name[type], value, prefix)
            jeżeli p.addtoken(type, value, (prefix, start)):
                jeżeli debug:
                    self.logger.debug("Stop.")
                przerwij
            prefix = ""
            lineno, column = end
            jeżeli value.endswith("\n"):
                lineno += 1
                column = 0
        inaczej:
            # We never broke out -- EOF jest too soon (how can this happen???)
            podnieś parse.ParseError("incomplete input",
                                   type, value, (prefix, start))
        zwróć p.rootnode

    def parse_stream_raw(self, stream, debug=Nieprawda):
        """Parse a stream oraz zwróć the syntax tree."""
        tokens = tokenize.generate_tokens(stream.readline)
        zwróć self.parse_tokens(tokens, debug)

    def parse_stream(self, stream, debug=Nieprawda):
        """Parse a stream oraz zwróć the syntax tree."""
        zwróć self.parse_stream_raw(stream, debug)

    def parse_file(self, filename, encoding=Nic, debug=Nieprawda):
        """Parse a file oraz zwróć the syntax tree."""
        stream = codecs.open(filename, "r", encoding)
        spróbuj:
            zwróć self.parse_stream(stream, debug)
        w_końcu:
            stream.close()

    def parse_string(self, text, debug=Nieprawda):
        """Parse a string oraz zwróć the syntax tree."""
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        zwróć self.parse_tokens(tokens, debug)


def load_grammar(gt="Grammar.txt", gp=Nic,
                 save=Prawda, force=Nieprawda, logger=Nic):
    """Load the grammar (maybe z a pickle)."""
    jeżeli logger jest Nic:
        logger = logging.getLogger()
    jeżeli gp jest Nic:
        head, tail = os.path.splitext(gt)
        jeżeli tail == ".txt":
            tail = ""
        gp = head + tail + ".".join(map(str, sys.version_info)) + ".pickle"
    jeżeli force albo nie _newer(gp, gt):
        logger.info("Generating grammar tables z %s", gt)
        g = pgen.generate_grammar(gt)
        jeżeli save:
            logger.info("Writing grammar tables to %s", gp)
            spróbuj:
                g.dump(gp)
            wyjąwszy OSError jako e:
                logger.info("Writing failed:"+str(e))
    inaczej:
        g = grammar.Grammar()
        g.load(gp)
    zwróć g


def _newer(a, b):
    """Inquire whether file a was written since file b."""
    jeżeli nie os.path.exists(a):
        zwróć Nieprawda
    jeżeli nie os.path.exists(b):
        zwróć Prawda
    zwróć os.path.getmtime(a) >= os.path.getmtime(b)


def main(*args):
    """Main program, when run jako a script: produce grammar pickle files.

    Calls load_grammar dla each argument, a path to a grammar text file.
    """
    jeżeli nie args:
        args = sys.argv[1:]
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(message)s')
    dla gt w args:
        load_grammar(gt, save=Prawda, force=Prawda)
    zwróć Prawda

jeżeli __name__ == "__main__":
    sys.exit(int(nie main()))
