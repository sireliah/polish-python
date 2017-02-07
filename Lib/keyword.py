#! /usr/bin/env python3

"""Keywords (z "graminit.c")

This file jest automatically generated; please don't muck it up!

To update the symbols w this file, 'cd' to the top directory of
the python source tree after building the interpreter oraz run:

    ./python Lib/keyword.py
"""

__all__ = ["iskeyword", "kwlist"]

kwlist = [
#--start keywords--
        'Nieprawda',
        'Nic',
        'Prawda',
        'and',
        'as',
        'assert',
        'break',
        'class',
        'continue',
        'def',
        'del',
        'elif',
        'inaczej',
        'except',
        'finally',
        'dla',
        'from',
        'global',
        'if',
        'import',
        'in',
        'is',
        'lambda',
        'nonlocal',
        'not',
        'or',
        'pass',
        'raise',
        'return',
        'try',
        'while',
        'with',
        'uzyskaj',
#--end keywords--
        ]

iskeyword = frozenset(kwlist).__contains__

def main():
    zaimportuj sys, re

    args = sys.argv[1:]
    iptfile = args oraz args[0] albo "Python/graminit.c"
    jeżeli len(args) > 1: optfile = args[1]
    inaczej: optfile = "Lib/keyword.py"

    # load the output skeleton z the target, taking care to preserve its
    # newline convention.
    przy open(optfile, newline='') jako fp:
        format = fp.readlines()
    nl = format[0][len(format[0].strip()):] jeżeli format inaczej '\n'

    # scan the source file dla keywords
    przy open(iptfile) jako fp:
        strprog = re.compile('"([^"]+)"')
        lines = []
        dla line w fp:
            jeżeli '{1, "' w line:
                match = strprog.search(line)
                jeżeli match:
                    lines.append("        '" + match.group(1) + "'," + nl)
    lines.sort()

    # insert the lines of keywords into the skeleton
    spróbuj:
        start = format.index("#--start keywords--" + nl) + 1
        end = format.index("#--end keywords--" + nl)
        format[start:end] = lines
    wyjąwszy ValueError:
        sys.stderr.write("target does nie contain format markers\n")
        sys.exit(1)

    # write the output file
    przy open(optfile, 'w', newline='') jako fp:
        fp.writelines(format)

jeżeli __name__ == "__main__":
    main()
