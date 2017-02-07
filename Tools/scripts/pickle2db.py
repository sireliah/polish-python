#!/usr/bin/env python3

"""
Synopsis: %(prog)s [-h|-b|-g|-r|-a|-d] [ picklefile ] dbfile

Read the given picklefile jako a series of key/value pairs oraz write to a new
database.  If the database already exists, any contents are deleted.  The
optional flags indicate the type of the output database:

    -a - open using dbm (open any supported format)
    -b - open jako bsddb btree file
    -d - open jako dbm.ndbm file
    -g - open jako dbm.gnu file
    -h - open jako bsddb hash file
    -r - open jako bsddb recno file

The default jest hash.  If a pickle file jest named it jest opened dla read
access.  If no pickle file jest named, the pickle input jest read z standard
input.

Note that recno databases can only contain integer keys, so you can't dump a
hash albo btree database using db2pickle.py oraz reconstitute it to a recno
database przy %(prog)s unless your keys are integers.

"""

zaimportuj getopt
spróbuj:
    zaimportuj bsddb
wyjąwszy ImportError:
    bsddb = Nic
spróbuj:
    zaimportuj dbm.ndbm jako dbm
wyjąwszy ImportError:
    dbm = Nic
spróbuj:
    zaimportuj dbm.gnu jako gdbm
wyjąwszy ImportError:
    gdbm = Nic
spróbuj:
    zaimportuj dbm.ndbm jako anydbm
wyjąwszy ImportError:
    anydbm = Nic
zaimportuj sys
spróbuj:
    zaimportuj pickle jako pickle
wyjąwszy ImportError:
    zaimportuj pickle

prog = sys.argv[0]

def usage():
    sys.stderr.write(__doc__ % globals())

def main(args):
    spróbuj:
        opts, args = getopt.getopt(args, "hbrdag",
                                   ["hash", "btree", "recno", "dbm", "anydbm",
                                    "gdbm"])
    wyjąwszy getopt.error:
        usage()
        zwróć 1

    jeżeli len(args) == 0 albo len(args) > 2:
        usage()
        zwróć 1
    albo_inaczej len(args) == 1:
        pfile = sys.stdin
        dbfile = args[0]
    inaczej:
        spróbuj:
            pfile = open(args[0], 'rb')
        wyjąwszy IOError:
            sys.stderr.write("Unable to open %s\n" % args[0])
            zwróć 1
        dbfile = args[1]

    dbopen = Nic
    dla opt, arg w opts:
        jeżeli opt w ("-h", "--hash"):
            spróbuj:
                dbopen = bsddb.hashopen
            wyjąwszy AttributeError:
                sys.stderr.write("bsddb module unavailable.\n")
                zwróć 1
        albo_inaczej opt w ("-b", "--btree"):
            spróbuj:
                dbopen = bsddb.btopen
            wyjąwszy AttributeError:
                sys.stderr.write("bsddb module unavailable.\n")
                zwróć 1
        albo_inaczej opt w ("-r", "--recno"):
            spróbuj:
                dbopen = bsddb.rnopen
            wyjąwszy AttributeError:
                sys.stderr.write("bsddb module unavailable.\n")
                zwróć 1
        albo_inaczej opt w ("-a", "--anydbm"):
            spróbuj:
                dbopen = anydbm.open
            wyjąwszy AttributeError:
                sys.stderr.write("dbm module unavailable.\n")
                zwróć 1
        albo_inaczej opt w ("-g", "--gdbm"):
            spróbuj:
                dbopen = gdbm.open
            wyjąwszy AttributeError:
                sys.stderr.write("dbm.gnu module unavailable.\n")
                zwróć 1
        albo_inaczej opt w ("-d", "--dbm"):
            spróbuj:
                dbopen = dbm.open
            wyjąwszy AttributeError:
                sys.stderr.write("dbm.ndbm module unavailable.\n")
                zwróć 1
    jeżeli dbopen jest Nic:
        jeżeli bsddb jest Nic:
            sys.stderr.write("bsddb module unavailable - ")
            sys.stderr.write("must specify dbtype.\n")
            zwróć 1
        inaczej:
            dbopen = bsddb.hashopen

    spróbuj:
        db = dbopen(dbfile, 'c')
    wyjąwszy bsddb.error:
        sys.stderr.write("Unable to open %s.  " % dbfile)
        sys.stderr.write("Check dla format albo version mismatch.\n")
        zwróć 1
    inaczej:
        dla k w list(db.keys()):
            usuń db[k]

    dopóki 1:
        spróbuj:
            (key, val) = pickle.load(pfile)
        wyjąwszy EOFError:
            przerwij
        db[key] = val

    db.close()
    pfile.close()

    zwróć 0

jeżeli __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
