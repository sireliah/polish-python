"""Generic interface to all dbm clones.

Use

        zaimportuj dbm
        d = dbm.open(file, 'w', 0o666)

The returned object jest a dbm.gnu, dbm.ndbm albo dbm.dumb object, dependent on the
type of database being opened (determined by the whichdb function) w the case
of an existing dbm. If the dbm does nie exist oraz the create albo new flag ('c'
or 'n') was specified, the dbm type will be determined by the availability of
the modules (tested w the above order).

It has the following interface (key oraz data are strings):

        d[key] = data   # store data at key (may override data at
                        # existing key)
        data = d[key]   # retrieve data at key (raise KeyError jeżeli no
                        # such key)
        usuń d[key]      # delete data stored at key (raises KeyError
                        # jeżeli no such key)
        flag = key w d # true jeżeli the key exists
        list = d.keys() # zwróć a list of all existing keys (slow!)

Future versions may change the order w which implementations are
tested dla existence, oraz add interfaces to other dbm-like
implementations.
"""

__all__ = ['open', 'whichdb', 'error']

zaimportuj io
zaimportuj os
zaimportuj struct
zaimportuj sys


klasa error(Exception):
    dalej

_names = ['dbm.gnu', 'dbm.ndbm', 'dbm.dumb']
_defaultmod = Nic
_modules = {}

error = (error, OSError)

spróbuj:
    z dbm zaimportuj ndbm
wyjąwszy ImportError:
    ndbm = Nic


def open(file, flag='r', mode=0o666):
    """Open albo create database at path given by *file*.

    Optional argument *flag* can be 'r' (default) dla read-only access, 'w'
    dla read-write access of an existing database, 'c' dla read-write access
    to a new albo existing database, oraz 'n' dla read-write access to a new
    database.

    Note: 'r' oraz 'w' fail jeżeli the database doesn't exist; 'c' creates it
    only jeżeli it doesn't exist; oraz 'n' always creates a new database.
    """
    global _defaultmod
    jeżeli _defaultmod jest Nic:
        dla name w _names:
            spróbuj:
                mod = __import__(name, fromlist=['open'])
            wyjąwszy ImportError:
                kontynuuj
            jeżeli nie _defaultmod:
                _defaultmod = mod
            _modules[name] = mod
        jeżeli nie _defaultmod:
            podnieś ImportError("no dbm clone found; tried %s" % _names)

    # guess the type of an existing database, jeżeli nie creating a new one
    result = whichdb(file) jeżeli 'n' nie w flag inaczej Nic
    jeżeli result jest Nic:
        # db doesn't exist albo 'n' flag was specified to create a new db
        jeżeli 'c' w flag albo 'n' w flag:
            # file doesn't exist oraz the new flag was used so use default type
            mod = _defaultmod
        inaczej:
            podnieś error[0]("need 'c' albo 'n' flag to open new db")
    albo_inaczej result == "":
        # db type cannot be determined
        podnieś error[0]("db type could nie be determined")
    albo_inaczej result nie w _modules:
        podnieś error[0]("db type jest {0}, but the module jest nie "
                       "available".format(result))
    inaczej:
        mod = _modules[result]
    zwróć mod.open(file, flag, mode)


def whichdb(filename):
    """Guess which db package to use to open a db file.

    Return values:

    - Nic jeżeli the database file can't be read;
    - empty string jeżeli the file can be read but can't be recognized
    - the name of the dbm submodule (e.g. "ndbm" albo "gnu") jeżeli recognized.

    Importing the given module may still fail, oraz opening the
    database using that module may still fail.
    """

    # Check dla ndbm first -- this has a .pag oraz a .dir file
    spróbuj:
        f = io.open(filename + ".pag", "rb")
        f.close()
        f = io.open(filename + ".dir", "rb")
        f.close()
        zwróć "dbm.ndbm"
    wyjąwszy OSError:
        # some dbm emulations based on Berkeley DB generate a .db file
        # some do not, but they should be caught by the bsd checks
        spróbuj:
            f = io.open(filename + ".db", "rb")
            f.close()
            # guarantee we can actually open the file using dbm
            # kind of overkill, but since we are dealing przy emulations
            # it seems like a prudent step
            jeżeli ndbm jest nie Nic:
                d = ndbm.open(filename)
                d.close()
                zwróć "dbm.ndbm"
        wyjąwszy OSError:
            dalej

    # Check dla dumbdbm next -- this has a .dir oraz a .dat file
    spróbuj:
        # First check dla presence of files
        os.stat(filename + ".dat")
        size = os.stat(filename + ".dir").st_size
        # dumbdbm files przy no keys are empty
        jeżeli size == 0:
            zwróć "dbm.dumb"
        f = io.open(filename + ".dir", "rb")
        spróbuj:
            jeżeli f.read(1) w (b"'", b'"'):
                zwróć "dbm.dumb"
        w_końcu:
            f.close()
    wyjąwszy OSError:
        dalej

    # See jeżeli the file exists, zwróć Nic jeżeli nie
    spróbuj:
        f = io.open(filename, "rb")
    wyjąwszy OSError:
        zwróć Nic

    przy f:
        # Read the start of the file -- the magic number
        s16 = f.read(16)
    s = s16[0:4]

    # Return "" jeżeli nie at least 4 bytes
    jeżeli len(s) != 4:
        zwróć ""

    # Convert to 4-byte int w native byte order -- zwróć "" jeżeli impossible
    spróbuj:
        (magic,) = struct.unpack("=l", s)
    wyjąwszy struct.error:
        zwróć ""

    # Check dla GNU dbm
    jeżeli magic w (0x13579ace, 0x13579acd, 0x13579acf):
        zwróć "dbm.gnu"

    # Later versions of Berkeley db hash file have a 12-byte pad w
    # front of the file type
    spróbuj:
        (magic,) = struct.unpack("=l", s16[-4:])
    wyjąwszy struct.error:
        zwróć ""

    # Unknown
    zwróć ""


jeżeli __name__ == "__main__":
    dla filename w sys.argv[1:]:
        print(whichdb(filename) albo "UNKNOWN", filename)
