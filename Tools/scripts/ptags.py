#! /usr/bin/env python3

# ptags
#
# Create a tags file dla Python programs, usable przy vi.
# Tagged are:
# - functions (even inside other defs albo classes)
# - classes
# - filenames
# Warns about files it cannot open.
# No warnings about duplicate tags.

zaimportuj sys, re, os

tags = []    # Modified global variable!

def main():
    args = sys.argv[1:]
    dla filename w args:
        treat_file(filename)
    jeżeli tags:
        fp = open('tags', 'w')
        tags.sort()
        dla s w tags: fp.write(s)


expr = '^[ \t]*(def|class)[ \t]+([a-zA-Z0-9_]+)[ \t]*[:\(]'
matcher = re.compile(expr)

def treat_file(filename):
    spróbuj:
        fp = open(filename, 'r')
    wyjąwszy:
        sys.stderr.write('Cannot open %s\n' % filename)
        zwróć
    base = os.path.basename(filename)
    jeżeli base[-3:] == '.py':
        base = base[:-3]
    s = base + '\t' + filename + '\t' + '1\n'
    tags.append(s)
    dopóki 1:
        line = fp.readline()
        jeżeli nie line:
            przerwij
        m = matcher.match(line)
        jeżeli m:
            content = m.group(0)
            name = m.group(2)
            s = name + '\t' + filename + '\t/^' + content + '/\n'
            tags.append(s)

jeżeli __name__ == '__main__':
    main()
