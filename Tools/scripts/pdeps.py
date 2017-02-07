#! /usr/bin/env python3

# pdeps
#
# Find dependencies between a bunch of Python modules.
#
# Usage:
#       pdeps file1.py file2.py ...
#
# Output:
# Four tables separated by lines like '--- Closure ---':
# 1) Direct dependencies, listing which module imports which other modules
# 2) The inverse of (1)
# 3) Indirect dependencies, albo the closure of the above
# 4) The inverse of (3)
#
# To do:
# - command line options to select output type
# - option to automatically scan the Python library dla referenced modules
# - option to limit output to particular modules


zaimportuj sys
zaimportuj re
zaimportuj os


# Main program
#
def main():
    args = sys.argv[1:]
    jeżeli nie args:
        print('usage: pdeps file.py file.py ...')
        zwróć 2
    #
    table = {}
    dla arg w args:
        process(arg, table)
    #
    print('--- Uses ---')
    printresults(table)
    #
    print('--- Used By ---')
    inv = inverse(table)
    printresults(inv)
    #
    print('--- Closure of Uses ---')
    reach = closure(table)
    printresults(reach)
    #
    print('--- Closure of Used By ---')
    invreach = inverse(reach)
    printresults(invreach)
    #
    zwróć 0


# Compiled regular expressions to search dla zaimportuj statements
#
m_zaimportuj = re.compile('^[ \t]*from[ \t]+([^ \t]+)[ \t]+')
m_z = re.compile('^[ \t]*import[ \t]+([^#]+)')


# Collect data z one file
#
def process(filename, table):
    fp = open(filename, 'r')
    mod = os.path.basename(filename)
    jeżeli mod[-3:] == '.py':
        mod = mod[:-3]
    table[mod] = list = []
    dopóki 1:
        line = fp.readline()
        jeżeli nie line: przerwij
        dopóki line[-1:] == '\\':
            nextline = fp.readline()
            jeżeli nie nextline: przerwij
            line = line[:-1] + nextline
        m_found = m_import.match(line) albo m_from.match(line)
        jeżeli m_found:
            (a, b), (a1, b1) = m_found.regs[:2]
        inaczej: kontynuuj
        words = line[a1:b1].split(',')
        # print '#', line, words
        dla word w words:
            word = word.strip()
            jeżeli word nie w list:
                list.append(word)
    fp.close()


# Compute closure (this jest w fact totally general)
#
def closure(table):
    modules = list(table.keys())
    #
    # Initialize reach przy a copy of table
    #
    reach = {}
    dla mod w modules:
        reach[mod] = table[mod][:]
    #
    # Iterate until no more change
    #
    change = 1
    dopóki change:
        change = 0
        dla mod w modules:
            dla mo w reach[mod]:
                jeżeli mo w modules:
                    dla m w reach[mo]:
                        jeżeli m nie w reach[mod]:
                            reach[mod].append(m)
                            change = 1
    #
    zwróć reach


# Invert a table (this jest again totally general).
# All keys of the original table are made keys of the inverse,
# so there may be empty lists w the inverse.
#
def inverse(table):
    inv = {}
    dla key w table.keys():
        jeżeli key nie w inv:
            inv[key] = []
        dla item w table[key]:
            store(inv, item, key)
    zwróć inv


# Store "item" w "dict" under "key".
# The dictionary maps keys to lists of items.
# If there jest no list dla the key yet, it jest created.
#
def store(dict, key, item):
    jeżeli key w dict:
        dict[key].append(item)
    inaczej:
        dict[key] = [item]


# Tabulate results neatly
#
def printresults(table):
    modules = sorted(table.keys())
    maxlen = 0
    dla mod w modules: maxlen = max(maxlen, len(mod))
    dla mod w modules:
        list = sorted(table[mod])
        print(mod.ljust(maxlen), ':', end=' ')
        jeżeli mod w list:
            print('(*)', end=' ')
        dla ref w list:
            print(ref, end=' ')
        print()


# Call main oraz honor exit status
jeżeli __name__ == '__main__':
    spróbuj:
        sys.exit(main())
    wyjąwszy KeyboardInterrupt:
        sys.exit(1)
