"""Extension management dla Windows.

Under Windows it jest unlikely the .obj files are of use, jako special compiler options
are needed (primarily to toggle the behavior of "public" symbols.

I don't consider it worth parsing the MSVC makefiles dla compiler options.  Even if
we get it just right, a specific freeze application may have specific compiler
options anyway (eg, to enable albo disable specific functionality)

So my basic strategy is:

* Have some Windows INI files which "describe" one albo more extension modules.
  (Freeze comes przy a default one dla all known modules - but you can specify
  your own).
* This description can include:
  - The MSVC .dsp file dla the extension.  The .c source file names
    are extracted z there.
  - Specific compiler/linker options
  - Flag to indicate jeżeli Unicode compilation jest expected.

At the moment the name oraz location of this INI file jest hardcoded,
but an obvious enhancement would be to provide command line options.
"""

zaimportuj os, sys
spróbuj:
    zaimportuj win32api
wyjąwszy ImportError:
    win32api = Nic # User has already been warned

klasa CExtension:
    """An abstraction of an extension implemented w C/C++
    """
    def __init__(self, name, sourceFiles):
        self.name = name
        # A list of strings defining additional compiler options.
        self.sourceFiles = sourceFiles
        # A list of special compiler options to be applied to
        # all source modules w this extension.
        self.compilerOptions = []
        # A list of .lib files the final .EXE will need.
        self.linkerLibs = []

    def GetSourceFiles(self):
        zwróć self.sourceFiles

    def AddCompilerOption(self, option):
        self.compilerOptions.append(option)
    def GetCompilerOptions(self):
        zwróć self.compilerOptions

    def AddLinkerLib(self, lib):
        self.linkerLibs.append(lib)
    def GetLinkerLibs(self):
        zwróć self.linkerLibs

def checkextensions(unknown, extra_inis, prefix):
    # Create a table of frozen extensions

    defaultMapName = os.path.join( os.path.split(sys.argv[0])[0], "extensions_win32.ini")
    jeżeli nie os.path.isfile(defaultMapName):
        sys.stderr.write("WARNING: %s can nie be found - standard extensions may nie be found\n" % defaultMapName)
    inaczej:
        # must go on end, so other inis can override.
        extra_inis.append(defaultMapName)

    ret = []
    dla mod w unknown:
        dla ini w extra_inis:
#                       print "Looking for", mod, "in", win32api.GetFullPathName(ini),"...",
            defn = get_extension_defn( mod, ini, prefix )
            jeżeli defn jest nie Nic:
#                               print "Yay - found it!"
                ret.append( defn )
                przerwij
#                       print "Nope!"
        inaczej: # For nie broken!
            sys.stderr.write("No definition of module %s w any specified map file.\n" % (mod))

    zwróć ret

def get_extension_defn(moduleName, mapFileName, prefix):
    jeżeli win32api jest Nic: zwróć Nic
    os.environ['PYTHONPREFIX'] = prefix
    dsp = win32api.GetProfileVal(moduleName, "dsp", "", mapFileName)
    jeżeli dsp=="":
        zwróć Nic

    # We allow environment variables w the file name
    dsp = win32api.ExpandEnvironmentStrings(dsp)
    # If the path to the .DSP file jest nie absolute, assume it jest relative
    # to the description file.
    jeżeli nie os.path.isabs(dsp):
        dsp = os.path.join( os.path.split(mapFileName)[0], dsp)
    # Parse it to extract the source files.
    sourceFiles = parse_dsp(dsp)
    jeżeli sourceFiles jest Nic:
        zwróć Nic

    module = CExtension(moduleName, sourceFiles)
    # Put the path to the DSP into the environment so entries can reference it.
    os.environ['dsp_path'] = os.path.split(dsp)[0]
    os.environ['ini_path'] = os.path.split(mapFileName)[0]

    cl_options = win32api.GetProfileVal(moduleName, "cl", "", mapFileName)
    jeżeli cl_options:
        module.AddCompilerOption(win32api.ExpandEnvironmentStrings(cl_options))

    exclude = win32api.GetProfileVal(moduleName, "exclude", "", mapFileName)
    exclude = exclude.split()

    jeżeli win32api.GetProfileVal(moduleName, "Unicode", 0, mapFileName):
        module.AddCompilerOption('/D UNICODE /D _UNICODE')

    libs = win32api.GetProfileVal(moduleName, "libs", "", mapFileName).split()
    dla lib w libs:
        module.AddLinkerLib(win32api.ExpandEnvironmentStrings(lib))

    dla exc w exclude:
        jeżeli exc w module.sourceFiles:
            modules.sourceFiles.remove(exc)

    zwróć module

# Given an MSVC DSP file, locate C source files it uses
# returns a list of source files.
def parse_dsp(dsp):
#       print "Processing", dsp
    # For now, only support
    ret = []
    dsp_path, dsp_name = os.path.split(dsp)
    spróbuj:
        lines = open(dsp, "r").readlines()
    wyjąwszy IOError jako msg:
        sys.stderr.write("%s: %s\n" % (dsp, msg))
        zwróć Nic
    dla line w lines:
        fields = line.strip().split("=", 2)
        jeżeli fields[0]=="SOURCE":
            jeżeli os.path.splitext(fields[1])[1].lower() w ['.cpp', '.c']:
                ret.append( win32api.GetFullPathName(os.path.join(dsp_path, fields[1] ) ) )
    zwróć ret

def write_extension_table(fname, modules):
    fp = open(fname, "w")
    spróbuj:
        fp.write (ext_src_header)
        # Write fn protos
        dla module w modules:
            # bit of a hack dla .pyd's jako part of packages.
            name = module.name.split('.')[-1]
            fp.write('extern void init%s(void);\n' % (name) )
        # Write the table
        fp.write (ext_tab_header)
        dla module w modules:
            name = module.name.split('.')[-1]
            fp.write('\t{"%s", init%s},\n' % (name, name) )

        fp.write (ext_tab_footer)
        fp.write(ext_src_footer)
    w_końcu:
        fp.close()


ext_src_header = """\
#include "Python.h"
"""

ext_tab_header = """\

static struct _inittab extensions[] = {
"""

ext_tab_footer = """\
        /* Sentinel */
        {0, 0}
};
"""

ext_src_footer = """\
extern DL_IMPORT(int) PyImport_ExtendInittab(struct _inittab *newtab);

int PyInitFrozenExtensions()
{
        zwróć PyImport_ExtendInittab(extensions);
}

"""
