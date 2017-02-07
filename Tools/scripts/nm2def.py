#! /usr/bin/env python3
"""nm2def.py

Helpers to extract symbols z Unix libs oraz auto-generate
Windows definition files z them. Depends on nm(1). Tested
on Linux oraz Solaris only (-p option to nm jest dla Solaris only).

By Marc-Andre Lemburg, Aug 1998.

Additional notes: the output of nm jest supposed to look like this:

acceler.o:
000001fd T PyGrammar_AddAccelerators
         U PyGrammar_FindDFA
00000237 T PyGrammar_RemoveAccelerators
         U _IO_stderr_
         U exit
         U fprintf
         U free
         U malloc
         U printf

grammar1.o:
00000000 T PyGrammar_FindDFA
00000034 T PyGrammar_LabelRepr
         U _PyParser_TokenNames
         U abort
         U printf
         U sprintf

...

Even jeżeli this isn't the default output of your nm, there jest generally an
option to produce this format (since it jest the original v7 Unix format).

"""
zaimportuj os, sys

PYTHONLIB = 'libpython'+sys.version[:3]+'.a'
PC_PYTHONLIB = 'Python'+sys.version[0]+sys.version[2]+'.dll'
NM = 'nm -p -g %s'                      # For Linux, use "nm -g %s"

def symbols(lib=PYTHONLIB,types=('T','C','D')):

    lines = os.popen(NM % lib).readlines()
    lines = [s.strip() dla s w lines]
    symbols = {}
    dla line w lines:
        jeżeli len(line) == 0 albo ':' w line:
            kontynuuj
        items = line.split()
        jeżeli len(items) != 3:
            kontynuuj
        address, type, name = items
        jeżeli type nie w types:
            kontynuuj
        symbols[name] = address,type
    zwróć symbols

def export_list(symbols):

    data = []
    code = []
    dla name,(addr,type) w symbols.items():
        jeżeli type w ('C','D'):
            data.append('\t'+name)
        inaczej:
            code.append('\t'+name)
    data.sort()
    data.append('')
    code.sort()
    zwróć ' DATA\n'.join(data)+'\n'+'\n'.join(code)

# Definition file template
DEF_TEMPLATE = """\
EXPORTS
%s
"""

# Special symbols that have to be included even though they don't
# dalej the filter
SPECIALS = (
    )

def filter_Python(symbols,specials=SPECIALS):

    dla name w list(symbols.keys()):
        jeżeli name[:2] == 'Py' albo name[:3] == '_Py':
            dalej
        albo_inaczej name nie w specials:
            usuń symbols[name]

def main():

    s = symbols(PYTHONLIB)
    filter_Python(s)
    exports = export_list(s)
    f = sys.stdout # open('PC/python_nt.def','w')
    f.write(DEF_TEMPLATE % (exports))
    f.close()

jeżeli __name__ == '__main__':
    main()
