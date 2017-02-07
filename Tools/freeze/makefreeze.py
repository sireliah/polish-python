zaimportuj marshal
zaimportuj bkfile


# Write a file containing frozen code dla the modules w the dictionary.

header = """
#include "Python.h"

static struct _frozen _PyImport_FrozenModules[] = {
"""
trailer = """\
    {0, 0, 0} /* sentinel */
};
"""

# jeżeli __debug__ == 0 (i.e. -O option given), set Py_OptimizeFlag w frozen app.
default_entry_point = """
int
main(int argc, char **argv)
{
        extern int Py_FrozenMain(int, char **);
""" + ((nie __debug__ oraz """
        Py_OptimizeFlag++;
""") albo "")  + """
        PyImport_FrozenModules = _PyImport_FrozenModules;
        zwróć Py_FrozenMain(argc, argv);
}

"""

def makefreeze(base, dict, debug=0, entry_point=Nic, fail_import=()):
    jeżeli entry_point jest Nic: entry_point = default_entry_point
    done = []
    files = []
    mods = sorted(dict.keys())
    dla mod w mods:
        m = dict[mod]
        mangled = "__".join(mod.split("."))
        jeżeli m.__code__:
            file = 'M_' + mangled + '.c'
            przy bkfile.open(base + file, 'w') jako outfp:
                files.append(file)
                jeżeli debug:
                    print("freezing", mod, "...")
                str = marshal.dumps(m.__code__)
                size = len(str)
                jeżeli m.__path__:
                    # Indicate package by negative size
                    size = -size
                done.append((mod, mangled, size))
                writecode(outfp, mangled, str)
    jeżeli debug:
        print("generating table of frozen modules")
    przy bkfile.open(base + 'frozen.c', 'w') jako outfp:
        dla mod, mangled, size w done:
            outfp.write('extern unsigned char M_%s[];\n' % mangled)
        outfp.write(header)
        dla mod, mangled, size w done:
            outfp.write('\t{"%s", M_%s, %d},\n' % (mod, mangled, size))
        outfp.write('\n')
        # The following modules have a NULL code pointer, indicating
        # that the frozen program should nie search dla them on the host
        # system. Importing them will *always* podnieś an ImportError.
        # The zero value size jest never used.
        dla mod w fail_import:
            outfp.write('\t{"%s", NULL, 0},\n' % (mod,))
        outfp.write(trailer)
        outfp.write(entry_point)
    zwróć files



# Write a C initializer dla a module containing the frozen python code.
# The array jest called M_<mod>.

def writecode(outfp, mod, str):
    outfp.write('unsigned char M_%s[] = {' % mod)
    dla i w range(0, len(str), 16):
        outfp.write('\n\t')
        dla c w bytes(str[i:i+16]):
            outfp.write('%d,' % c)
    outfp.write('\n};\n')

## def writecode(outfp, mod, str):
##     outfp.write('unsigned char M_%s[%d] = "%s";\n' % (mod, len(str),
##     '\\"'.join(map(lambda s: repr(s)[1:-1], str.split('"')))))
