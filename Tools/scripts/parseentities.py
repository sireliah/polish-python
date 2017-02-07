#!/usr/bin/env python3
""" Utility dla parsing HTML entity definitions available from:

      http://www.w3.org/ jako e.g.
      http://www.w3.org/TR/REC-html40/HTMLlat1.ent

    Input jest read z stdin, output jest written to stdout w form of a
    Python snippet defining a dictionary "entitydefs" mapping literal
    entity name to character albo numeric entity.

    Marc-Andre Lemburg, mal@lemburg.com, 1999.
    Use jako you like. NO WARRANTIES.

"""
zaimportuj re,sys

entityRE = re.compile('<!ENTITY +(\w+) +CDATA +"([^"]+)" +-- +((?:.|\n)+?) *-->')

def parse(text,pos=0,endpos=Nic):

    pos = 0
    jeżeli endpos jest Nic:
        endpos = len(text)
    d = {}
    dopóki 1:
        m = entityRE.search(text,pos,endpos)
        jeżeli nie m:
            przerwij
        name,charcode,comment = m.groups()
        d[name] = charcode,comment
        pos = m.end()
    zwróć d

def writefile(f,defs):

    f.write("entitydefs = {\n")
    items = sorted(defs.items())
    dla name, (charcode,comment) w items:
        jeżeli charcode[:2] == '&#':
            code = int(charcode[2:-1])
            jeżeli code < 256:
                charcode = "'\%o'" % code
            inaczej:
                charcode = repr(charcode)
        inaczej:
            charcode = repr(charcode)
        comment = ' '.join(comment.split())
        f.write("    '%s':\t%s,  \t# %s\n" % (name,charcode,comment))
    f.write('\n}\n')

jeżeli __name__ == '__main__':
    jeżeli len(sys.argv) > 1:
        infile = open(sys.argv[1])
    inaczej:
        infile = sys.stdin
    jeżeli len(sys.argv) > 2:
        outfile = open(sys.argv[2],'w')
    inaczej:
        outfile = sys.stdout
    text = infile.read()
    defs = parse(text)
    writefile(outfile,defs)
