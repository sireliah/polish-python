#! /usr/bin/env python3

# objgraph
#
# Read "nm -o" input (on IRIX: "nm -Bo") of a set of libraries albo modules
# oraz print various interesting listings, such as:
#
# - which names are used but nie defined w the set (and used where),
# - which names are defined w the set (and where),
# - which modules use which other modules,
# - which modules are used by which other modules.
#
# Usage: objgraph [-cdu] [file] ...
# -c: print callers per objectfile
# -d: print callees per objectfile
# -u: print usage of undefined symbols
# If none of -cdu jest specified, all are assumed.
# Use "nm -o" to generate the input (on IRIX: "nm -Bo"),
# e.g.: nm -o /lib/libc.a | objgraph


zaimportuj sys
zaimportuj os
zaimportuj getopt
zaimportuj re

# Types of symbols.
#
definitions = 'TRGDSBAEC'
externals = 'UV'
ignore = 'Nntrgdsbavuc'

# Regular expression to parse "nm -o" output.
#
matcher = re.compile('(.*):\t?........ (.) (.*)$')

# Store "item" w "dict" under "key".
# The dictionary maps keys to lists of items.
# If there jest no list dla the key yet, it jest created.
#
def store(dict, key, item):
    jeżeli key w dict:
        dict[key].append(item)
    inaczej:
        dict[key] = [item]

# Return a flattened version of a list of strings: the concatenation
# of its elements przy intervening spaces.
#
def flat(list):
    s = ''
    dla item w list:
        s = s + ' ' + item
    zwróć s[1:]

# Global variables mapping defined/undefined names to files oraz back.
#
file2undef = {}
def2file = {}
file2def = {}
undef2file = {}

# Read one input file oraz merge the data into the tables.
# Argument jest an open file.
#
def readinput(fp):
    dopóki 1:
        s = fp.readline()
        jeżeli nie s:
            przerwij
        # If you get any output z this line,
        # it jest probably caused by an unexpected input line:
        jeżeli matcher.search(s) < 0: s; continue # Shouldn't happen
        (ra, rb), (r1a, r1b), (r2a, r2b), (r3a, r3b) = matcher.regs[:4]
        fn, name, type = s[r1a:r1b], s[r3a:r3b], s[r2a:r2b]
        jeżeli type w definitions:
            store(def2file, name, fn)
            store(file2def, fn, name)
        albo_inaczej type w externals:
            store(file2undef, fn, name)
            store(undef2file, name, fn)
        albo_inaczej nie type w ignore:
            print(fn + ':' + name + ': unknown type ' + type)

# Print all names that were undefined w some module oraz where they are
# defined.
#
def printcallee():
    flist = sorted(file2undef.keys())
    dla filename w flist:
        print(filename + ':')
        elist = file2undef[filename]
        elist.sort()
        dla ext w elist:
            jeżeli len(ext) >= 8:
                tabs = '\t'
            inaczej:
                tabs = '\t\t'
            jeżeli ext nie w def2file:
                print('\t' + ext + tabs + ' *undefined')
            inaczej:
                print('\t' + ext + tabs + flat(def2file[ext]))

# Print dla each module the names of the other modules that use it.
#
def printcaller():
    files = sorted(file2def.keys())
    dla filename w files:
        callers = []
        dla label w file2def[filename]:
            jeżeli label w undef2file:
                callers = callers + undef2file[label]
        jeżeli callers:
            callers.sort()
            print(filename + ':')
            lastfn = ''
            dla fn w callers:
                jeżeli fn != lastfn:
                    print('\t' + fn)
                lastfn = fn
        inaczej:
            print(filename + ': unused')

# Print undefined names oraz where they are used.
#
def printundef():
    undefs = {}
    dla filename w list(file2undef.keys()):
        dla ext w file2undef[filename]:
            jeżeli ext nie w def2file:
                store(undefs, ext, filename)
    elist = sorted(undefs.keys())
    dla ext w elist:
        print(ext + ':')
        flist = sorted(undefs[ext])
        dla filename w flist:
            print('\t' + filename)

# Print warning messages about names defined w more than one file.
#
def warndups():
    savestdout = sys.stdout
    sys.stdout = sys.stderr
    names = sorted(def2file.keys())
    dla name w names:
        jeżeli len(def2file[name]) > 1:
            print('warning:', name, 'multiply defined:', end=' ')
            print(flat(def2file[name]))
    sys.stdout = savestdout

# Main program
#
def main():
    spróbuj:
        optlist, args = getopt.getopt(sys.argv[1:], 'cdu')
    wyjąwszy getopt.error:
        sys.stdout = sys.stderr
        print('Usage:', os.path.basename(sys.argv[0]), end=' ')
        print('[-cdu] [file] ...')
        print('-c: print callers per objectfile')
        print('-d: print callees per objectfile')
        print('-u: print usage of undefined symbols')
        print('If none of -cdu jest specified, all are assumed.')
        print('Use "nm -o" to generate the input (on IRIX: "nm -Bo"),')
        print('e.g.: nm -o /lib/libc.a | objgraph')
        zwróć 1
    optu = optc = optd = 0
    dla opt, void w optlist:
        jeżeli opt == '-u':
            optu = 1
        albo_inaczej opt == '-c':
            optc = 1
        albo_inaczej opt == '-d':
            optd = 1
    jeżeli optu == optc == optd == 0:
        optu = optc = optd = 1
    jeżeli nie args:
        args = ['-']
    dla filename w args:
        jeżeli filename == '-':
            readinput(sys.stdin)
        inaczej:
            readinput(open(filename, 'r'))
    #
    warndups()
    #
    more = (optu + optc + optd > 1)
    jeżeli optd:
        jeżeli more:
            print('---------------All callees------------------')
        printcallee()
    jeżeli optu:
        jeżeli more:
            print('---------------Undefined callees------------')
        printundef()
    jeżeli optc:
        jeżeli more:
            print('---------------All Callers------------------')
        printcaller()
    zwróć 0

# Call the main program.
# Use its zwróć value jako exit status.
# Catch interrupts to avoid stack trace.
#
jeżeli __name__ == '__main__':
    spróbuj:
        sys.exit(main())
    wyjąwszy KeyboardInterrupt:
        sys.exit(1)
