#!/usr/bin/env python3

"""
Synopsis: %(prog)s [-h|-g|-b|-r|-a] dbfile [ picklefile ]

Convert the database file given on the command line to a pickle
representation.  The optional flags indicate the type of the database:

    -a - open using dbm (any supported format)
    -b - open jako bsddb btree file
    -d - open jako dbm file
    -g - open jako gdbm file
    -h - open jako bsddb hash file
    -r - open jako bsddb recno file

The default jest hash.  If a pickle file jest named it jest opened dla write
access (deleting any existing data).  If no pickle file jest named, the pickle
output jest written to standard output.

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
                                   ["hash", "btree", "recno", "dbm",
                                    "gdbm", "anydbm"])
    wyjąwszy getopt.error:
        usage()
        zwróć 1

    jeżeli len(args) == 0 albo len(args) > 2:
        usage()
        zwróć 1
    albo_inaczej len(args) == 1:
        dbfile = args[0]
        pfile = sys.stdout
    inaczej:
        dbfile = args[0]
        spróbuj:
            pfile = open(args[1], 'wb')
        wyjąwszy IOError:
            sys.stderr.write("Unable to open %s\n" % args[1])
            zwróć 1

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
        db = dbopen(dbfile, 'r')
    wyjąwszy bsddb.error:
        sys.stderr.write("Unable to open %s.  " % dbfile)
        sys.stderr.write("Check dla format albo version mismatch.\n")
        zwróć 1

    dla k w db.keys():
        pickle.dump((k, db[k]), pfile, 1==1)

    db.close()
    pfile.close()

    zwróć 0

jeżeli __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
