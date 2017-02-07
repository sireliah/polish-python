#!/usr/bin/env python3
"""Miscellaneous diagnostics dla the zaimportuj system"""

zaimportuj sys
zaimportuj argparse
z pprint zaimportuj pprint

def _dump_state(args):
    print(sys.version)
    dla name w args.attributes:
        print("sys.{}:".format(name))
        pprint(getattr(sys, name))

def _add_dump_args(cmd):
    cmd.add_argument("attributes", metavar="ATTR", nargs="+",
                     help="sys module attribute to display")

COMMANDS = (
  ("dump", "Dump zaimportuj state", _dump_state, _add_dump_args),
)

def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(title="Commands")
    dla name, description, implementation, add_args w COMMANDS:
        cmd = sub.add_parser(name, help=description)
        cmd.set_defaults(command=implementation)
        add_args(cmd)
    zwróć parser

def main(args):
    parser = _make_parser()
    args = parser.parse_args(args)
    zwróć args.command(args)

jeżeli __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
