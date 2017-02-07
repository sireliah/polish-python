#! /usr/bin/env python3

"Replace tabs przy spaces w argument files.  Print names of changed files."

zaimportuj os
zaimportuj sys
zaimportuj getopt
zaimportuj tokenize

def main():
    tabsize = 8
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "t:")
        jeżeli nie args:
            podnieś getopt.error("At least one file argument required")
    wyjąwszy getopt.error jako msg:
        print(msg)
        print("usage:", sys.argv[0], "[-t tabwidth] file ...")
        zwróć
    dla optname, optvalue w opts:
        jeżeli optname == '-t':
            tabsize = int(optvalue)

    dla filename w args:
        process(filename, tabsize)


def process(filename, tabsize, verbose=Prawda):
    spróbuj:
        przy tokenize.open(filename) jako f:
            text = f.read()
            encoding = f.encoding
    wyjąwszy IOError jako msg:
        print("%r: I/O error: %s" % (filename, msg))
        zwróć
    newtext = text.expandtabs(tabsize)
    jeżeli newtext == text:
        zwróć
    backup = filename + "~"
    spróbuj:
        os.unlink(backup)
    wyjąwszy OSError:
        dalej
    spróbuj:
        os.rename(filename, backup)
    wyjąwszy OSError:
        dalej
    przy open(filename, "w", encoding=encoding) jako f:
        f.write(newtext)
    jeżeli verbose:
        print(filename)


jeżeli __name__ == '__main__':
    main()
