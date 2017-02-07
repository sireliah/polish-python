#! /usr/bin/env python3
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>

"""Generate binary message catalog z textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This jest essentially the same function jako the
GNU msgfmt program, however, it jest a simpler implementation.

Usage: msgfmt.py [OPTIONS] filename.po

Options:
    -o file
    --output-file=file
        Specify the output file to write to.  If omitted, output will go to a
        file named filename.mo (based off the input file name).

    -h
    --help
        Print this message oraz exit.

    -V
    --version
        Display version information oraz exit.
"""

zaimportuj os
zaimportuj sys
zaimportuj ast
zaimportuj getopt
zaimportuj struct
zaimportuj array
z email.parser zaimportuj HeaderParser

__version__ = "1.1"

MESSAGES = {}



def usage(code, msg=''):
    print(__doc__, file=sys.stderr)
    jeżeli msg:
        print(msg, file=sys.stderr)
    sys.exit(code)



def add(id, str, fuzzy):
    "Add a non-fuzzy translation to the dictionary."
    global MESSAGES
    jeżeli nie fuzzy oraz str:
        MESSAGES[id] = str



def generate():
    "Return the generated output."
    global MESSAGES
    # the keys are sorted w the .mo file
    keys = sorted(MESSAGES.keys())
    offsets = []
    ids = strs = b''
    dla id w keys:
        # For each string, we need size oraz file offset.  Each string jest NUL
        # terminated; the NUL does nie count into the size.
        offsets.append((len(ids), len(id), len(strs), len(MESSAGES[id])))
        ids += id + b'\0'
        strs += MESSAGES[id] + b'\0'
    output = ''
    # The header jest 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # oraz the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    dla o1, l1, o2, l2 w offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412de,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size oraz offset of hash table
    output += array.array("i", offsets).tostring()
    output += ids
    output += strs
    zwróć output



def make(filename, outfile):
    ID = 1
    STR = 2

    # Compute .mo name z .po name oraz arguments
    jeżeli filename.endswith('.po'):
        infile = filename
    inaczej:
        infile = filename + '.po'
    jeżeli outfile jest Nic:
        outfile = os.path.splitext(infile)[0] + '.mo'

    spróbuj:
        lines = open(infile, 'rb').readlines()
    wyjąwszy IOError jako msg:
        print(msg, file=sys.stderr)
        sys.exit(1)

    section = Nic
    fuzzy = 0

    # Start off assuming Latin-1, so everything decodes without failure,
    # until we know the exact encoding
    encoding = 'latin-1'

    # Parse the catalog
    lno = 0
    dla l w lines:
        l = l.decode(encoding)
        lno += 1
        # If we get a comment line after a msgstr, this jest a new entry
        jeżeli l[0] == '#' oraz section == STR:
            add(msgid, msgstr, fuzzy)
            section = Nic
            fuzzy = 0
        # Record a fuzzy mark
        jeżeli l[:2] == '#,' oraz 'fuzzy' w l:
            fuzzy = 1
        # Skip comments
        jeżeli l[0] == '#':
            kontynuuj
        # Now we are w a msgid section, output previous section
        jeżeli l.startswith('msgid') oraz nie l.startswith('msgid_plural'):
            jeżeli section == STR:
                add(msgid, msgstr, fuzzy)
                jeżeli nie msgid:
                    # See whether there jest an encoding declaration
                    p = HeaderParser()
                    charset = p.parsestr(msgstr.decode(encoding)).get_content_charset()
                    jeżeli charset:
                        encoding = charset
            section = ID
            l = l[5:]
            msgid = msgstr = b''
            is_plural = Nieprawda
        # This jest a message przy plural forms
        albo_inaczej l.startswith('msgid_plural'):
            jeżeli section != ID:
                print('msgid_plural nie preceded by msgid on %s:%d' % (infile, lno),
                      file=sys.stderr)
                sys.exit(1)
            l = l[12:]
            msgid += b'\0' # separator of singular oraz plural
            is_plural = Prawda
        # Now we are w a msgstr section
        albo_inaczej l.startswith('msgstr'):
            section = STR
            jeżeli l.startswith('msgstr['):
                jeżeli nie is_plural:
                    print('plural without msgid_plural on %s:%d' % (infile, lno),
                          file=sys.stderr)
                    sys.exit(1)
                l = l.split(']', 1)[1]
                jeżeli msgstr:
                    msgstr += b'\0' # Separator of the various plural forms
            inaczej:
                jeżeli is_plural:
                    print('indexed msgstr required dla plural on  %s:%d' % (infile, lno),
                          file=sys.stderr)
                    sys.exit(1)
                l = l[6:]
        # Skip empty lines
        l = l.strip()
        jeżeli nie l:
            kontynuuj
        l = ast.literal_eval(l)
        jeżeli section == ID:
            msgid += l.encode(encoding)
        albo_inaczej section == STR:
            msgstr += l.encode(encoding)
        inaczej:
            print('Syntax error on %s:%d' % (infile, lno), \
                  'before:', file=sys.stderr)
            print(l, file=sys.stderr)
            sys.exit(1)
    # Add last entry
    jeżeli section == STR:
        add(msgid, msgstr, fuzzy)

    # Compute output
    output = generate()

    spróbuj:
        open(outfile,"wb").write(output)
    wyjąwszy IOError jako msg:
        print(msg, file=sys.stderr)



def main():
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'hVo:',
                                   ['help', 'version', 'output-file='])
    wyjąwszy getopt.error jako msg:
        usage(1, msg)

    outfile = Nic
    # parse options
    dla opt, arg w opts:
        jeżeli opt w ('-h', '--help'):
            usage(0)
        albo_inaczej opt w ('-V', '--version'):
            print("msgfmt.py", __version__)
            sys.exit(0)
        albo_inaczej opt w ('-o', '--output-file'):
            outfile = arg
    # do it
    jeżeli nie args:
        print('No input file given', file=sys.stderr)
        print("Try `msgfmt --help' dla more information.", file=sys.stderr)
        zwróć

    dla filename w args:
        make(filename, outfile)


jeżeli __name__ == '__main__':
    main()
