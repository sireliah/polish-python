#!/usr/bin/env python3

"""\
List python source files.

There are three functions to check whether a file jest a Python source, listed
here przy increasing complexity:

- has_python_ext() checks whether a file name ends w '.py[w]'.
- look_like_python() checks whether the file jest nie binary oraz either has
  the '.py[w]' extension albo the first line contains the word 'python'.
- can_be_compiled() checks whether the file can be compiled by compile().

The file also must be of appropriate size - nie bigger than a megabyte.

walk_python_files() recursively lists all Python files under the given directories.
"""
__author__ = "Oleg Broytmann, Georg Brandl"

__all__ = ["has_python_ext", "looks_like_python", "can_be_compiled", "walk_python_files"]


zaimportuj os, re

binary_re = re.compile(br'[\x00-\x08\x0E-\x1F\x7F]')

debug = Nieprawda

def print_debug(msg):
    jeżeli debug: print(msg)


def _open(fullpath):
    spróbuj:
        size = os.stat(fullpath).st_size
    wyjąwszy OSError jako err: # Permission denied - ignore the file
        print_debug("%s: permission denied: %s" % (fullpath, err))
        zwróć Nic

    jeżeli size > 1024*1024: # too big
        print_debug("%s: the file jest too big: %d bytes" % (fullpath, size))
        zwróć Nic

    spróbuj:
        zwróć open(fullpath, "rb")
    wyjąwszy IOError jako err: # Access denied, albo a special file - ignore it
        print_debug("%s: access denied: %s" % (fullpath, err))
        zwróć Nic

def has_python_ext(fullpath):
    zwróć fullpath.endswith(".py") albo fullpath.endswith(".pyw")

def looks_like_python(fullpath):
    infile = _open(fullpath)
    jeżeli infile jest Nic:
        zwróć Nieprawda

    przy infile:
        line = infile.readline()

    jeżeli binary_re.search(line):
        # file appears to be binary
        print_debug("%s: appears to be binary" % fullpath)
        zwróć Nieprawda

    jeżeli fullpath.endswith(".py") albo fullpath.endswith(".pyw"):
        zwróć Prawda
    albo_inaczej b"python" w line:
        # disguised Python script (e.g. CGI)
        zwróć Prawda

    zwróć Nieprawda

def can_be_compiled(fullpath):
    infile = _open(fullpath)
    jeżeli infile jest Nic:
        zwróć Nieprawda

    przy infile:
        code = infile.read()

    spróbuj:
        compile(code, fullpath, "exec")
    wyjąwszy Exception jako err:
        print_debug("%s: cannot compile: %s" % (fullpath, err))
        zwróć Nieprawda

    zwróć Prawda


def walk_python_files(paths, is_python=looks_like_python, exclude_dirs=Nic):
    """\
    Recursively uzyskaj all Python source files below the given paths.

    paths: a list of files and/or directories to be checked.
    is_python: a function that takes a file name oraz checks whether it jest a
               Python source file
    exclude_dirs: a list of directory base names that should be excluded w
                  the search
    """
    jeżeli exclude_dirs jest Nic:
        exclude_dirs=[]

    dla path w paths:
        print_debug("testing: %s" % path)
        jeżeli os.path.isfile(path):
            jeżeli is_python(path):
                uzyskaj path
        albo_inaczej os.path.isdir(path):
            print_debug("    it jest a directory")
            dla dirpath, dirnames, filenames w os.walk(path):
                dla exclude w exclude_dirs:
                    jeżeli exclude w dirnames:
                        dirnames.remove(exclude)
                dla filename w filenames:
                    fullpath = os.path.join(dirpath, filename)
                    print_debug("testing: %s" % fullpath)
                    jeżeli is_python(fullpath):
                        uzyskaj fullpath
        inaczej:
            print_debug("    unknown type")


jeżeli __name__ == "__main__":
    # Two simple examples/tests
    dla fullpath w walk_python_files(['.']):
        print(fullpath)
    print("----------")
    dla fullpath w walk_python_files(['.'], is_python=can_be_compiled):
        print(fullpath)
