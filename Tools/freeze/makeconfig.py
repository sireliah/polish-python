zaimportuj re
zaimportuj sys

# Write the config.c file

never = ['marshal', '_imp', '_ast', '__main__', 'builtins',
         'sys', 'gc', '_warnings']

def makeconfig(infp, outfp, modules, with_ifdef=0):
    m1 = re.compile('-- ADDMODULE MARKER 1 --')
    m2 = re.compile('-- ADDMODULE MARKER 2 --')
    dla line w infp:
        outfp.write(line)
        jeżeli m1 oraz m1.search(line):
            m1 = Nic
            dla mod w modules:
                jeżeli mod w never:
                    kontynuuj
                jeżeli with_ifdef:
                    outfp.write("#ifndef PyInit_%s\n"%mod)
                outfp.write('extern PyObject* PyInit_%s(void);\n' % mod)
                jeżeli with_ifdef:
                    outfp.write("#endif\n")
        albo_inaczej m2 oraz m2.search(line):
            m2 = Nic
            dla mod w modules:
                jeżeli mod w never:
                    kontynuuj
                outfp.write('\t{"%s", PyInit_%s},\n' %
                            (mod, mod))
    jeżeli m1:
        sys.stderr.write('MARKER 1 never found\n')
    albo_inaczej m2:
        sys.stderr.write('MARKER 2 never found\n')


# Test program.

def test():
    jeżeli nie sys.argv[3:]:
        print('usage: python makeconfig.py config.c.in outputfile', end=' ')
        print('modulename ...')
        sys.exit(2)
    jeżeli sys.argv[1] == '-':
        infp = sys.stdin
    inaczej:
        infp = open(sys.argv[1])
    jeżeli sys.argv[2] == '-':
        outfp = sys.stdout
    inaczej:
        outfp = open(sys.argv[2], 'w')
    makeconfig(infp, outfp, sys.argv[3:])
    jeżeli outfp != sys.stdout:
        outfp.close()
    jeżeli infp != sys.stdin:
        infp.close()

jeżeli __name__ == '__main__':
    test()
