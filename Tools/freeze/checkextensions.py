# Check dla a module w a set of extension directories.
# An extension directory should contain a Setup file
# oraz one albo more .o files albo a lib.a file.

zaimportuj os
zaimportuj parsesetup

def checkextensions(unknown, extensions):
    files = []
    modules = []
    edict = {}
    dla e w extensions:
        setup = os.path.join(e, 'Setup')
        liba = os.path.join(e, 'lib.a')
        jeżeli nie os.path.isfile(liba):
            liba = Nic
        edict[e] = parsesetup.getsetupinfo(setup), liba
    dla mod w unknown:
        dla e w extensions:
            (mods, vars), liba = edict[e]
            jeżeli mod nie w mods:
                kontynuuj
            modules.append(mod)
            jeżeli liba:
                # If we find a lib.a, use it, ignore the
                # .o files, oraz use *all* libraries for
                # *all* modules w the Setup file
                jeżeli liba w files:
                    przerwij
                files.append(liba)
                dla m w list(mods.keys()):
                    files = files + select(e, mods, vars,
                                           m, 1)
                przerwij
            files = files + select(e, mods, vars, mod, 0)
            przerwij
    zwróć files, modules

def select(e, mods, vars, mod, skipofiles):
    files = []
    dla w w mods[mod]:
        w = treatword(w)
        jeżeli nie w:
            kontynuuj
        w = expandvars(w, vars)
        dla w w w.split():
            jeżeli skipofiles oraz w[-2:] == '.o':
                kontynuuj
            # Assume $var expands to absolute pathname
            jeżeli w[0] nie w ('-', '$') oraz w[-2:] w ('.o', '.a'):
                w = os.path.join(e, w)
            jeżeli w[:2] w ('-L', '-R') oraz w[2:3] != '$':
                w = w[:2] + os.path.join(e, w[2:])
            files.append(w)
    zwróć files

cc_flags = ['-I', '-D', '-U']
cc_exts = ['.c', '.C', '.cc', '.c++']

def treatword(w):
    jeżeli w[:2] w cc_flags:
        zwróć Nic
    jeżeli w[:1] == '-':
        zwróć w # Assume loader flag
    head, tail = os.path.split(w)
    base, ext = os.path.splitext(tail)
    jeżeli ext w cc_exts:
        tail = base + '.o'
        w = os.path.join(head, tail)
    zwróć w

def expandvars(str, vars):
    i = 0
    dopóki i < len(str):
        i = k = str.find('$', i)
        jeżeli i < 0:
            przerwij
        i = i+1
        var = str[i:i+1]
        i = i+1
        jeżeli var == '(':
            j = str.find(')', i)
            jeżeli j < 0:
                przerwij
            var = str[i:j]
            i = j+1
        jeżeli var w vars:
            str = str[:k] + vars[var] + str[i:]
            i = k
    zwróć str
