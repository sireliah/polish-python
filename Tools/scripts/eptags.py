#! /usr/bin/env python3
"""Create a TAGS file dla Python programs, usable przy GNU Emacs.

usage: eptags pyfiles...

The output TAGS file jest usable przy Emacs version 18, 19, 20.
Tagged are:
 - functions (even inside other defs albo classes)
 - classes

eptags warns about files it cannot open.
eptags will nie give warnings about duplicate tags.

BUGS:
   Because of tag duplication (methods przy the same name w different
   classes), TAGS files are nie very useful dla most object-oriented
   python projects.
"""
zaimportuj sys,re

expr = r'^[ \t]*(def|class)[ \t]+([a-zA-Z_][a-zA-Z0-9_]*)[ \t]*[:\(]'
matcher = re.compile(expr)

def treat_file(filename, outfp):
    """Append tags found w file named 'filename' to the open file 'outfp'"""
    spróbuj:
        fp = open(filename, 'r')
    wyjąwszy OSError:
        sys.stderr.write('Cannot open %s\n'%filename)
        zwróć
    charno = 0
    lineno = 0
    tags = []
    size = 0
    dopóki 1:
        line = fp.readline()
        jeżeli nie line:
            przerwij
        lineno = lineno + 1
        m = matcher.search(line)
        jeżeli m:
            tag = m.group(0) + '\177%d,%d\n' % (lineno, charno)
            tags.append(tag)
            size = size + len(tag)
        charno = charno + len(line)
    outfp.write('\f\n%s,%d\n' % (filename,size))
    dla tag w tags:
        outfp.write(tag)

def main():
    outfp = open('TAGS', 'w')
    dla filename w sys.argv[1:]:
        treat_file(filename, outfp)

jeżeli __name__=="__main__":
    main()
