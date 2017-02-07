"""Mailcap file handling.  See RFC 1524."""

zaimportuj os

__all__ = ["getcaps","findmatch"]

# Part 1: top-level interface.

def getcaps():
    """Return a dictionary containing the mailcap database.

    The dictionary maps a MIME type (in all lowercase, e.g. 'text/plain')
    to a list of dictionaries corresponding to mailcap entries.  The list
    collects all the entries dla that MIME type z all available mailcap
    files.  Each dictionary contains key-value pairs dla that MIME type,
    where the viewing command jest stored przy the key "view".

    """
    caps = {}
    dla mailcap w listmailcapfiles():
        spróbuj:
            fp = open(mailcap, 'r')
        wyjąwszy OSError:
            kontynuuj
        przy fp:
            morecaps = readmailcapfile(fp)
        dla key, value w morecaps.items():
            jeżeli nie key w caps:
                caps[key] = value
            inaczej:
                caps[key] = caps[key] + value
    zwróć caps

def listmailcapfiles():
    """Return a list of all mailcap files found on the system."""
    # This jest mostly a Unix thing, but we use the OS path separator anyway
    jeżeli 'MAILCAPS' w os.environ:
        pathstr = os.environ['MAILCAPS']
        mailcaps = pathstr.split(os.pathsep)
    inaczej:
        jeżeli 'HOME' w os.environ:
            home = os.environ['HOME']
        inaczej:
            # Don't bother przy getpwuid()
            home = '.' # Last resort
        mailcaps = [home + '/.mailcap', '/etc/mailcap',
                '/usr/etc/mailcap', '/usr/local/etc/mailcap']
    zwróć mailcaps


# Part 2: the parser.

def readmailcapfile(fp):
    """Read a mailcap file oraz zwróć a dictionary keyed by MIME type.

    Each MIME type jest mapped to an entry consisting of a list of
    dictionaries; the list will contain more than one such dictionary
    jeżeli a given MIME type appears more than once w the mailcap file.
    Each dictionary contains key-value pairs dla that MIME type, where
    the viewing command jest stored przy the key "view".
    """
    caps = {}
    dopóki 1:
        line = fp.readline()
        jeżeli nie line: przerwij
        # Ignore comments oraz blank lines
        jeżeli line[0] == '#' albo line.strip() == '':
            kontynuuj
        nextline = line
        # Join continuation lines
        dopóki nextline[-2:] == '\\\n':
            nextline = fp.readline()
            jeżeli nie nextline: nextline = '\n'
            line = line[:-2] + nextline
        # Parse the line
        key, fields = parseline(line)
        jeżeli nie (key oraz fields):
            kontynuuj
        # Normalize the key
        types = key.split('/')
        dla j w range(len(types)):
            types[j] = types[j].strip()
        key = '/'.join(types).lower()
        # Update the database
        jeżeli key w caps:
            caps[key].append(fields)
        inaczej:
            caps[key] = [fields]
    zwróć caps

def parseline(line):
    """Parse one entry w a mailcap file oraz zwróć a dictionary.

    The viewing command jest stored jako the value przy the key "view",
    oraz the rest of the fields produce key-value pairs w the dict.
    """
    fields = []
    i, n = 0, len(line)
    dopóki i < n:
        field, i = parsefield(line, i, n)
        fields.append(field)
        i = i+1 # Skip semicolon
    jeżeli len(fields) < 2:
        zwróć Nic, Nic
    key, view, rest = fields[0], fields[1], fields[2:]
    fields = {'view': view}
    dla field w rest:
        i = field.find('=')
        jeżeli i < 0:
            fkey = field
            fvalue = ""
        inaczej:
            fkey = field[:i].strip()
            fvalue = field[i+1:].strip()
        jeżeli fkey w fields:
            # Ignore it
            dalej
        inaczej:
            fields[fkey] = fvalue
    zwróć key, fields

def parsefield(line, i, n):
    """Separate one key-value pair w a mailcap entry."""
    start = i
    dopóki i < n:
        c = line[i]
        jeżeli c == ';':
            przerwij
        albo_inaczej c == '\\':
            i = i+2
        inaczej:
            i = i+1
    zwróć line[start:i].strip(), i


# Part 3: using the database.

def findmatch(caps, MIMEtype, key='view', filename="/dev/null", plist=[]):
    """Find a match dla a mailcap entry.

    Return a tuple containing the command line, oraz the mailcap entry
    used; (Nic, Nic) jeżeli no match jest found.  This may invoke the
    'test' command of several matching entries before deciding which
    entry to use.

    """
    entries = lookup(caps, MIMEtype, key)
    # XXX This code should somehow check dla the needsterminal flag.
    dla e w entries:
        jeżeli 'test' w e:
            test = subst(e['test'], filename, plist)
            jeżeli test oraz os.system(test) != 0:
                kontynuuj
        command = subst(e[key], MIMEtype, filename, plist)
        zwróć command, e
    zwróć Nic, Nic

def lookup(caps, MIMEtype, key=Nic):
    entries = []
    jeżeli MIMEtype w caps:
        entries = entries + caps[MIMEtype]
    MIMEtypes = MIMEtype.split('/')
    MIMEtype = MIMEtypes[0] + '/*'
    jeżeli MIMEtype w caps:
        entries = entries + caps[MIMEtype]
    jeżeli key jest nie Nic:
        entries = [e dla e w entries jeżeli key w e]
    zwróć entries

def subst(field, MIMEtype, filename, plist=[]):
    # XXX Actually, this jest Unix-specific
    res = ''
    i, n = 0, len(field)
    dopóki i < n:
        c = field[i]; i = i+1
        jeżeli c != '%':
            jeżeli c == '\\':
                c = field[i:i+1]; i = i+1
            res = res + c
        inaczej:
            c = field[i]; i = i+1
            jeżeli c == '%':
                res = res + c
            albo_inaczej c == 's':
                res = res + filename
            albo_inaczej c == 't':
                res = res + MIMEtype
            albo_inaczej c == '{':
                start = i
                dopóki i < n oraz field[i] != '}':
                    i = i+1
                name = field[start:i]
                i = i+1
                res = res + findparam(name, plist)
            # XXX To do:
            # %n == number of parts jeżeli type jest multipart/*
            # %F == list of alternating type oraz filename dla parts
            inaczej:
                res = res + '%' + c
    zwróć res

def findparam(name, plist):
    name = name.lower() + '='
    n = len(name)
    dla p w plist:
        jeżeli p[:n].lower() == name:
            zwróć p[n:]
    zwróć ''


# Part 4: test program.

def test():
    zaimportuj sys
    caps = getcaps()
    jeżeli nie sys.argv[1:]:
        show(caps)
        zwróć
    dla i w range(1, len(sys.argv), 2):
        args = sys.argv[i:i+2]
        jeżeli len(args) < 2:
            print("usage: mailcap [MIMEtype file] ...")
            zwróć
        MIMEtype = args[0]
        file = args[1]
        command, e = findmatch(caps, MIMEtype, 'view', file)
        jeżeli nie command:
            print("No viewer found for", type)
        inaczej:
            print("Executing:", command)
            sts = os.system(command)
            jeżeli sts:
                print("Exit status:", sts)

def show(caps):
    print("Mailcap files:")
    dla fn w listmailcapfiles(): print("\t" + fn)
    print()
    jeżeli nie caps: caps = getcaps()
    print("Mailcap entries:")
    print()
    ckeys = sorted(caps)
    dla type w ckeys:
        print(type)
        entries = caps[type]
        dla e w entries:
            keys = sorted(e)
            dla k w keys:
                print("  %-15s" % k, e[k])
            print()

jeżeli __name__ == '__main__':
    test()
