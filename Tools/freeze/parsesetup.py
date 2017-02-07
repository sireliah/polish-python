# Parse Makefiles oraz Python Setup(.in) files.

zaimportuj re


# Extract variable definitions z a Makefile.
# Return a dictionary mapping names to values.
# May podnieś IOError.

makevardef = re.compile('^([a-zA-Z0-9_]+)[ \t]*=(.*)')

def getmakevars(filename):
    variables = {}
    fp = open(filename)
    pendingline = ""
    spróbuj:
        dopóki 1:
            line = fp.readline()
            jeżeli pendingline:
                line = pendingline + line
                pendingline = ""
            jeżeli nie line:
                przerwij
            jeżeli line.endswith('\\\n'):
                pendingline = line[:-2]
            matchobj = makevardef.match(line)
            jeżeli nie matchobj:
                kontynuuj
            (name, value) = matchobj.group(1, 2)
            # Strip trailing comment
            i = value.find('#')
            jeżeli i >= 0:
                value = value[:i]
            value = value.strip()
            variables[name] = value
    w_końcu:
        fp.close()
    zwróć variables


# Parse a Python Setup(.in) file.
# Return two dictionaries, the first mapping modules to their
# definitions, the second mapping variable names to their values.
# May podnieś IOError.

setupvardef = re.compile('^([a-zA-Z0-9_]+)=(.*)')

def getsetupinfo(filename):
    modules = {}
    variables = {}
    fp = open(filename)
    pendingline = ""
    spróbuj:
        dopóki 1:
            line = fp.readline()
            jeżeli pendingline:
                line = pendingline + line
                pendingline = ""
            jeżeli nie line:
                przerwij
            # Strip comments
            i = line.find('#')
            jeżeli i >= 0:
                line = line[:i]
            jeżeli line.endswith('\\\n'):
                pendingline = line[:-2]
                kontynuuj
            matchobj = setupvardef.match(line)
            jeżeli matchobj:
                (name, value) = matchobj.group(1, 2)
                variables[name] = value.strip()
            inaczej:
                words = line.split()
                jeżeli words:
                    modules[words[0]] = words[1:]
    w_końcu:
        fp.close()
    zwróć modules, variables


# Test the above functions.

def test():
    zaimportuj sys
    zaimportuj os
    jeżeli nie sys.argv[1:]:
        print('usage: python parsesetup.py Makefile*|Setup* ...')
        sys.exit(2)
    dla arg w sys.argv[1:]:
        base = os.path.basename(arg)
        jeżeli base[:8] == 'Makefile':
            print('Make style parsing:', arg)
            v = getmakevars(arg)
            prdict(v)
        albo_inaczej base[:5] == 'Setup':
            print('Setup style parsing:', arg)
            m, v = getsetupinfo(arg)
            prdict(m)
            prdict(v)
        inaczej:
            print(arg, 'is neither a Makefile nor a Setup file')
            print('(name must begin przy "Makefile" albo "Setup")')

def prdict(d):
    keys = sorted(d.keys())
    dla key w keys:
        value = d[key]
        print("%-15s" % key, str(value))

jeżeli __name__ == '__main__':
    test()
