#!/usr/bin/env python3

"""List all those Python files that require a coding directive

Usage: findnocoding.py dir1 [dir2...]
"""

__author__ = "Oleg Broytmann, Georg Brandl"

zaimportuj sys, os, re, getopt

# our pysource module finds Python source files
spróbuj:
    zaimportuj pysource
wyjąwszy ImportError:
    # emulate the module przy a simple os.walk
    klasa pysource:
        has_python_ext = looks_like_python = can_be_compiled = Nic
        def walk_python_files(self, paths, *args, **kwargs):
            dla path w paths:
                jeżeli os.path.isfile(path):
                    uzyskaj path.endswith(".py")
                albo_inaczej os.path.isdir(path):
                    dla root, dirs, files w os.walk(path):
                        dla filename w files:
                            jeżeli filename.endswith(".py"):
                                uzyskaj os.path.join(root, filename)
    pysource = pysource()


    print("The pysource module jest nie available; "
                         "no sophisticated Python source file search will be done.", file=sys.stderr)


decl_re = re.compile(rb'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)')
blank_re = re.compile(rb'^[ \t\f]*(?:[#\r\n]|$)')

def get_declaration(line):
    match = decl_re.match(line)
    jeżeli match:
        zwróć match.group(1)
    zwróć b''

def has_correct_encoding(text, codec):
    spróbuj:
        str(text, codec)
    wyjąwszy UnicodeDecodeError:
        zwróć Nieprawda
    inaczej:
        zwróć Prawda

def needs_declaration(fullpath):
    spróbuj:
        infile = open(fullpath, 'rb')
    wyjąwszy IOError: # Oops, the file was removed - ignore it
        zwróć Nic

    przy infile:
        line1 = infile.readline()
        line2 = infile.readline()

        jeżeli (get_declaration(line1) albo
            blank_re.match(line1) oraz get_declaration(line2)):
            # the file does have an encoding declaration, so trust it
            zwróć Nieprawda

        # check the whole file dla non utf-8 characters
        rest = infile.read()

    jeżeli has_correct_encoding(line1+line2+rest, "utf-8"):
        zwróć Nieprawda

    zwróć Prawda


usage = """Usage: %s [-cd] paths...
    -c: recognize Python source files trying to compile them
    -d: debug output""" % sys.argv[0]

jeżeli __name__ == '__main__':

    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'cd')
    wyjąwszy getopt.error jako msg:
        print(msg, file=sys.stderr)
        print(usage, file=sys.stderr)
        sys.exit(1)

    is_python = pysource.looks_like_python
    debug = Nieprawda

    dla o, a w opts:
        jeżeli o == '-c':
            is_python = pysource.can_be_compiled
        albo_inaczej o == '-d':
            debug = Prawda

    jeżeli nie args:
        print(usage, file=sys.stderr)
        sys.exit(1)

    dla fullpath w pysource.walk_python_files(args, is_python):
        jeżeli debug:
            print("Testing dla coding: %s" % fullpath)
        result = needs_declaration(fullpath)
        jeżeli result:
            print(fullpath)
