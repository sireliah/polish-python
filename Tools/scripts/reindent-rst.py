#!/usr/bin/env python3

# Make a reST file compliant to our pre-commit hook.
# Currently just remove trailing whitespace.

zaimportuj sys

zaimportuj patchcheck

def main(argv=sys.argv):
    patchcheck.normalize_docs_whitespace(argv[1:])

jeżeli __name__ == '__main__':
    sys.exit(main())
