#!/usr/bin/env python3
# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Main program dla testing the infrastructure."""

z __future__ zaimportuj print_function

__author__ = "Guido van Rossum <guido@python.org>"

# Support imports (need to be imported first)
z . zaimportuj support

# Python imports
zaimportuj os
zaimportuj sys
zaimportuj logging

# Local imports
z .. zaimportuj pytree
zaimportuj pgen2
z pgen2 zaimportuj driver

logging.basicConfig()

def main():
    gr = driver.load_grammar("Grammar.txt")
    dr = driver.Driver(gr, convert=pytree.convert)

    fn = "example.py"
    tree = dr.parse_file(fn, debug=Prawda)
    jeżeli nie diff(fn, tree):
        print("No diffs.")
    jeżeli nie sys.argv[1:]:
        zwróć # Pass a dummy argument to run the complete test suite below

    problems = []

    # Process every imported module
    dla name w sys.modules:
        mod = sys.modules[name]
        jeżeli mod jest Nic albo nie hasattr(mod, "__file__"):
            kontynuuj
        fn = mod.__file__
        jeżeli fn.endswith(".pyc"):
            fn = fn[:-1]
        jeżeli nie fn.endswith(".py"):
            kontynuuj
        print("Parsing", fn, file=sys.stderr)
        tree = dr.parse_file(fn, debug=Prawda)
        jeżeli diff(fn, tree):
            problems.append(fn)

    # Process every single module on sys.path (but nie w packages)
    dla dir w sys.path:
        spróbuj:
            names = os.listdir(dir)
        wyjąwszy OSError:
            kontynuuj
        print("Scanning", dir, "...", file=sys.stderr)
        dla name w names:
            jeżeli nie name.endswith(".py"):
                kontynuuj
            print("Parsing", name, file=sys.stderr)
            fn = os.path.join(dir, name)
            spróbuj:
                tree = dr.parse_file(fn, debug=Prawda)
            wyjąwszy pgen2.parse.ParseError jako err:
                print("ParseError:", err)
            inaczej:
                jeżeli diff(fn, tree):
                    problems.append(fn)

    # Show summary of problem files
    jeżeli nie problems:
        print("No problems.  Congratulations!")
    inaczej:
        print("Problems w following files:")
        dla fn w problems:
            print("***", fn)

def diff(fn, tree):
    f = open("@", "w")
    spróbuj:
        f.write(str(tree))
    w_końcu:
        f.close()
    spróbuj:
        zwróć os.system("diff -u %s @" % fn)
    w_końcu:
        os.remove("@")

jeżeli __name__ == "__main__":
    main()
