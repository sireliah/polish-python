#! /usr/bin/env python3
# Script dla preparing OpenSSL dla building on Windows.
# Uses Perl to create nmake makefiles oraz otherwise prepare the way
# dla building on 32 albo 64 bit platforms.

# Script originally authored by Mark Hammond.
# Major revisions by:
#   Martin v. Löwis
#   Christian Heimes
#   Zachary Ware

# THEORETICALLY, you can:
# * Unpack the latest OpenSSL release where $(opensslDir) w
#   PCbuild\pyproject.props expects it to be.
# * Install ActivePerl oraz ensure it jest somewhere on your path.
# * Run this script przy the OpenSSL source dir jako the only argument.
#
# it should configure OpenSSL such that it jest ready to be built by
# ssl.vcxproj on 32 albo 64 bit platforms.

zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj shutil
zaimportuj subprocess

# Find all "foo.exe" files on the PATH.
def find_all_on_path(filename, extras = Nic):
    entries = os.environ["PATH"].split(os.pathsep)
    ret = []
    dla p w entries:
        fname = os.path.abspath(os.path.join(p, filename))
        jeżeli os.path.isfile(fname) oraz fname nie w ret:
            ret.append(fname)
    jeżeli extras:
        dla p w extras:
            fname = os.path.abspath(os.path.join(p, filename))
            jeżeli os.path.isfile(fname) oraz fname nie w ret:
                ret.append(fname)
    zwróć ret

# Find a suitable Perl installation dla OpenSSL.
# cygwin perl does *not* work.  ActivePerl does.
# Being a Perl dummy, the simplest way I can check jest jeżeli the "Win32" package
# jest available.
def find_working_perl(perls):
    dla perl w perls:
        spróbuj:
            subprocess.check_output([perl, "-e", "use Win32;"])
        wyjąwszy subprocess.CalledProcessError:
            kontynuuj
        inaczej:
            zwróć perl

    jeżeli perls:
        print("The following perl interpreters were found:")
        dla p w perls:
            print(" ", p)
        print(" Nic of these versions appear suitable dla building OpenSSL")
    inaczej:
        print("NO perl interpreters were found on this machine at all!")
    print(" Please install ActivePerl oraz ensure it appears on your path")

def create_makefile64(makefile, m32):
    """Create oraz fix makefile dla 64bit

    Replace 32 przy 64bit directories
    """
    jeżeli nie os.path.isfile(m32):
        zwróć
    przy open(m32) jako fin:
        przy open(makefile, 'w') jako fout:
            dla line w fin:
                line = line.replace("=tmp32", "=tmp64")
                line = line.replace("=out32", "=out64")
                line = line.replace("=inc32", "=inc64")
                # force 64 bit machine
                line = line.replace("MKLIB=lib", "MKLIB=lib /MACHINE:X64")
                line = line.replace("LFLAGS=", "LFLAGS=/MACHINE:X64 ")
                # don't link against the lib on 64bit systems
                line = line.replace("bufferoverflowu.lib", "")
                fout.write(line)
    os.unlink(m32)

def create_asms(makefile):
    #create a custom makefile out of the provided one
    asm_makefile = os.path.splitext(makefile)[0] + '.asm.mak'
    przy open(makefile) jako fin:
        przy open(asm_makefile, 'w') jako fout:
            dla line w fin:
                # Keep everything up to the install target (it's convenient)
                jeżeli line.startswith('install: all'):
                    przerwij
                inaczej:
                    fout.write(line)
            asms = []
            dla line w fin:
                jeżeli '.asm' w line oraz line.strip().endswith('.pl'):
                    asms.append(line.split(':')[0])
                    dopóki line.strip():
                        fout.write(line)
                        line = next(fin)
                    fout.write('\n')

            fout.write('asms: $(TMP_D) ')
            fout.write(' '.join(asms))
            fout.write('\n')

    os.system('nmake /f {} PERL=perl asms'.format(asm_makefile))
    os.unlink(asm_makefile)



def fix_makefile(makefile):
    """Fix some stuff w all makefiles
    """
    jeżeli nie os.path.isfile(makefile):
        zwróć
    copy_if_different = r'$(PERL) $(SRC_D)\util\copy-if-different.pl'
    przy open(makefile) jako fin:
        lines = fin.readlines()
    przy open(makefile, 'w') jako fout:
        dla line w lines:
            jeżeli line.startswith("PERL="):
                kontynuuj
            jeżeli line.startswith("CP="):
                line = "CP=copy\n"
            jeżeli line.startswith("MKDIR="):
                line = "MKDIR=mkdir\n"
            jeżeli line.startswith("CFLAG="):
                line = line.strip()
                dla algo w ("RC5", "MDC2", "IDEA"):
                    noalgo = " -DOPENSSL_NO_%s" % algo
                    jeżeli noalgo nie w line:
                        line = line + noalgo
                line = line + '\n'
            jeżeli copy_if_different w line:
                line = line.replace(copy_if_different, 'copy /Y')
            fout.write(line)

def run_configure(configure, do_script):
    print("perl Configure "+configure+" no-idea no-mdc2")
    os.system("perl Configure "+configure+" no-idea no-mdc2")
    print(do_script)
    os.system(do_script)

def cmp(f1, f2):
    bufsize = 1024 * 8
    przy open(f1, 'rb') jako fp1, open(f2, 'rb') jako fp2:
        dopóki Prawda:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            jeżeli b1 != b2:
                zwróć Nieprawda
            jeżeli nie b1:
                zwróć Prawda

def copy(src, dst):
    jeżeli os.path.isfile(dst) oraz cmp(src, dst):
        zwróć
    shutil.copy(src, dst)

def prep(arch):
    jeżeli arch == "x86":
        configure = "VC-WIN32"
        do_script = "ms\\do_nasm"
        makefile="ms\\nt.mak"
        m32 = makefile
        dirsuffix = "32"
    albo_inaczej arch == "amd64":
        configure = "VC-WIN64A"
        do_script = "ms\\do_win64a"
        makefile = "ms\\nt64.mak"
        m32 = makefile.replace('64', '')
        dirsuffix = "64"
        #os.environ["VSEXTCOMP_USECL"] = "MS_OPTERON"
    inaczej:
        podnieś ValueError('Unrecognized platform: %s' % arch)

    # rebuild makefile when we do the role over z 32 to 64 build
    jeżeli arch == "amd64" oraz os.path.isfile(m32) oraz nie os.path.isfile(makefile):
        os.unlink(m32)

    # If the ssl makefiles do nie exist, we invoke Perl to generate them.
    # Due to a bug w this script, the makefile sometimes ended up empty
    # Force a regeneration jeżeli it is.
    jeżeli nie os.path.isfile(makefile) albo os.path.getsize(makefile)==0:
        print("Creating the makefiles...")
        sys.stdout.flush()
        run_configure(configure, do_script)

        jeżeli arch == "amd64":
            create_makefile64(makefile, m32)
        fix_makefile(makefile)
        copy(r"crypto\buildinf.h", r"crypto\buildinf_%s.h" % arch)
        copy(r"crypto\opensslconf.h", r"crypto\opensslconf_%s.h" % arch)
    inaczej:
        print(makefile, 'already exists!')

    print('creating asms...')
    create_asms(makefile)

def main():
    jeżeli len(sys.argv) == 1:
        print("Not enough arguments: directory containing OpenSSL",
              "sources must be supplied")
        sys.exit(1)

    jeżeli len(sys.argv) > 2:
        print("Too many arguments supplied, all we need jest the directory",
              "containing OpenSSL sources")
        sys.exit(1)

    ssl_dir = sys.argv[1]

    jeżeli nie os.path.isdir(ssl_dir):
        print(ssl_dir, "is nie an existing directory!")
        sys.exit(1)

    # perl should be on the path, but we also look w "\perl" oraz "c:\\perl"
    # jako "well known" locations
    perls = find_all_on_path("perl.exe", [r"\perl\bin",
                                          r"C:\perl\bin",
                                          r"\perl64\bin",
                                          r"C:\perl64\bin",
                                         ])
    perl = find_working_perl(perls)
    jeżeli perl:
        print("Found a working perl at '%s'" % (perl,))
    inaczej:
        sys.exit(1)
    sys.stdout.flush()

    # Put our working Perl at the front of our path
    os.environ["PATH"] = os.path.dirname(perl) + \
                                os.pathsep + \
                                os.environ["PATH"]

    old_cwd = os.getcwd()
    spróbuj:
        os.chdir(ssl_dir)
        dla arch w ['amd64', 'x86']:
            prep(arch)
    w_końcu:
        os.chdir(old_cwd)

jeżeli __name__=='__main__':
    main()
