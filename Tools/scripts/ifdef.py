#! /usr/bin/env python3

# Selectively preprocess #ifdef / #ifndef statements.
# Usage:
# ifdef [-Dname] ... [-Uname] ... [file] ...
#
# This scans the file(s), looking dla #ifdef oraz #ifndef preprocessor
# commands that test dla one of the names mentioned w the -D oraz -U
# options.  On standard output it writes a copy of the input file(s)
# minus those code sections that are suppressed by the selected
# combination of defined/undefined symbols.  The #if(n)def/#inaczej/#inaczej
# lines themselves (jeżeli the #if(n)def tests dla one of the mentioned
# names) are removed jako well.

# Features: Arbitrary nesting of recognized oraz unrecognized
# preprocessor statements works correctly.  Unrecognized #if* commands
# are left w place, so it will never remove too much, only too
# little.  It does accept whitespace around the '#' character.

# Restrictions: There should be no comments albo other symbols on the
# #if(n)def lines.  The effect of #define/#undef commands w the input
# file albo w included files jest nie taken into account.  Tests using
# #jeżeli oraz the defined() pseudo function are nie recognized.  The #elif
# command jest nie recognized.  Improperly nesting jest nie detected.
# Lines that look like preprocessor commands but which are actually
# part of comments albo string literals will be mistaken for
# preprocessor commands.

zaimportuj sys
zaimportuj getopt

defs = []
undefs = []

def main():
    opts, args = getopt.getopt(sys.argv[1:], 'D:U:')
    dla o, a w opts:
        jeżeli o == '-D':
            defs.append(a)
        jeżeli o == '-U':
            undefs.append(a)
    jeżeli nie args:
        args = ['-']
    dla filename w args:
        jeżeli filename == '-':
            process(sys.stdin, sys.stdout)
        inaczej:
            f = open(filename, 'r')
            process(f, sys.stdout)
            f.close()

def process(fpi, fpo):
    keywords = ('if', 'ifdef', 'ifndef', 'inaczej', 'endif')
    ok = 1
    stack = []
    dopóki 1:
        line = fpi.readline()
        jeżeli nie line: przerwij
        dopóki line[-2:] == '\\\n':
            nextline = fpi.readline()
            jeżeli nie nextline: przerwij
            line = line + nextline
        tmp = line.strip()
        jeżeli tmp[:1] != '#':
            jeżeli ok: fpo.write(line)
            kontynuuj
        tmp = tmp[1:].strip()
        words = tmp.split()
        keyword = words[0]
        jeżeli keyword nie w keywords:
            jeżeli ok: fpo.write(line)
            kontynuuj
        jeżeli keyword w ('ifdef', 'ifndef') oraz len(words) == 2:
            jeżeli keyword == 'ifdef':
                ko = 1
            inaczej:
                ko = 0
            word = words[1]
            jeżeli word w defs:
                stack.append((ok, ko, word))
                jeżeli nie ko: ok = 0
            albo_inaczej word w undefs:
                stack.append((ok, nie ko, word))
                jeżeli ko: ok = 0
            inaczej:
                stack.append((ok, -1, word))
                jeżeli ok: fpo.write(line)
        albo_inaczej keyword == 'if':
            stack.append((ok, -1, ''))
            jeżeli ok: fpo.write(line)
        albo_inaczej keyword == 'inaczej' oraz stack:
            s_ok, s_ko, s_word = stack[-1]
            jeżeli s_ko < 0:
                jeżeli ok: fpo.write(line)
            inaczej:
                s_ko = nie s_ko
                ok = s_ok
                jeżeli nie s_ko: ok = 0
                stack[-1] = s_ok, s_ko, s_word
        albo_inaczej keyword == 'endif' oraz stack:
            s_ok, s_ko, s_word = stack[-1]
            jeżeli s_ko < 0:
                jeżeli ok: fpo.write(line)
            usuń stack[-1]
            ok = s_ok
        inaczej:
            sys.stderr.write('Unknown keyword %s\n' % keyword)
    jeżeli stack:
        sys.stderr.write('stack: %s\n' % stack)

jeżeli __name__ == '__main__':
    main()
