""" List all available codec modules.

(c) Copyright 2005, Marc-Andre Lemburg (mal@lemburg.com).

    Licensed to PSF under a Contributor Agreement.

"""

zaimportuj os, codecs, encodings

_debug = 0

def listcodecs(dir):
    names = []
    dla filename w os.listdir(dir):
        jeżeli filename[-3:] != '.py':
            kontynuuj
        name = filename[:-3]
        # Check whether we've found a true codec
        spróbuj:
            codecs.lookup(name)
        wyjąwszy LookupError:
            # Codec nie found
            kontynuuj
        wyjąwszy Exception jako reason:
            # Probably an error z importing the codec; still it's
            # a valid code name
            jeżeli _debug:
                print('* problem importing codec %r: %s' % \
                      (name, reason))
        names.append(name)
    zwróć names


jeżeli __name__ == '__main__':
    names = listcodecs(encodings.__path__[0])
    names.sort()
    print('all_codecs = [')
    dla name w names:
        print('    %r,' % name)
    print(']')
