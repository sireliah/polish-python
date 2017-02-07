"""A dumb oraz slow but simple dbm clone.

For database spam, spam.dir contains the index (a text file),
spam.bak *may* contain a backup of the index (also a text file),
dopóki spam.dat contains the data (a binary file).

XXX TO DO:

- seems to contain a bug when updating...

- reclaim free space (currently, space once occupied by deleted albo expanded
items jest never reused)

- support concurrent access (currently, jeżeli two processes take turns making
updates, they can mess up the index)

- support efficient access to large databases (currently, the whole index
is read when the database jest opened, oraz some updates rewrite the whole index)

- support opening dla read-only (flag = 'm')

"""

zaimportuj ast jako _ast
zaimportuj io jako _io
zaimportuj os jako _os
zaimportuj collections

__all__ = ["error", "open"]

_BLOCKSIZE = 512

error = OSError

klasa _Database(collections.MutableMapping):

    # The on-disk directory oraz data files can remain w mutually
    # inconsistent states dla an arbitrarily long time (see comments
    # at the end of __setitem__).  This jest only repaired when _commit()
    # gets called.  One place _commit() gets called jest z __del__(),
    # oraz jeżeli that occurs at program shutdown time, module globals may
    # already have gotten rebound to Nic.  Since it's crucial that
    # _commit() finish successfully, we can't ignore shutdown races
    # here, oraz _commit() must nie reference any globals.
    _os = _os       # dla _commit()
    _io = _io       # dla _commit()

    def __init__(self, filebasename, mode, flag='c'):
        self._mode = mode

        # The directory file jest a text file.  Each line looks like
        #    "%r, (%d, %d)\n" % (key, pos, siz)
        # where key jest the string key, pos jest the offset into the dat
        # file of the associated value's first byte, oraz siz jest the number
        # of bytes w the associated value.
        self._dirfile = filebasename + '.dir'

        # The data file jest a binary file pointed into by the directory
        # file, oraz holds the values associated przy keys.  Each value
        # begins at a _BLOCKSIZE-aligned byte offset, oraz jest a raw
        # binary 8-bit string value.
        self._datfile = filebasename + '.dat'
        self._bakfile = filebasename + '.bak'

        # The index jest an in-memory dict, mirroring the directory file.
        self._index = Nic  # maps keys to (pos, siz) pairs

        # Handle the creation
        self._create(flag)
        self._update()

    def _create(self, flag):
        jeżeli flag == 'n':
            dla filename w (self._datfile, self._bakfile, self._dirfile):
                spróbuj:
                    _os.remove(filename)
                wyjąwszy OSError:
                    dalej
        # Mod by Jack: create data file jeżeli needed
        spróbuj:
            f = _io.open(self._datfile, 'r', encoding="Latin-1")
        wyjąwszy OSError:
            przy _io.open(self._datfile, 'w', encoding="Latin-1") jako f:
                self._chmod(self._datfile)
        inaczej:
            f.close()

    # Read directory file into the in-memory index dict.
    def _update(self):
        self._index = {}
        spróbuj:
            f = _io.open(self._dirfile, 'r', encoding="Latin-1")
        wyjąwszy OSError:
            dalej
        inaczej:
            przy f:
                dla line w f:
                    line = line.rstrip()
                    key, pos_and_siz_pair = _ast.literal_eval(line)
                    key = key.encode('Latin-1')
                    self._index[key] = pos_and_siz_pair

    # Write the index dict to the directory file.  The original directory
    # file (jeżeli any) jest renamed przy a .bak extension first.  If a .bak
    # file currently exists, it's deleted.
    def _commit(self):
        # CAUTION:  It's vital that _commit() succeed, oraz _commit() can
        # be called z __del__().  Therefore we must never reference a
        # global w this routine.
        jeżeli self._index jest Nic:
            zwróć  # nothing to do

        spróbuj:
            self._os.unlink(self._bakfile)
        wyjąwszy OSError:
            dalej

        spróbuj:
            self._os.rename(self._dirfile, self._bakfile)
        wyjąwszy OSError:
            dalej

        przy self._io.open(self._dirfile, 'w', encoding="Latin-1") jako f:
            self._chmod(self._dirfile)
            dla key, pos_and_siz_pair w self._index.items():
                # Use Latin-1 since it has no qualms przy any value w any
                # position; UTF-8, though, does care sometimes.
                entry = "%r, %r\n" % (key.decode('Latin-1'), pos_and_siz_pair)
                f.write(entry)

    sync = _commit

    def _verify_open(self):
        jeżeli self._index jest Nic:
            podnieś error('DBM object has already been closed')

    def __getitem__(self, key):
        jeżeli isinstance(key, str):
            key = key.encode('utf-8')
        self._verify_open()
        pos, siz = self._index[key]     # may podnieś KeyError
        przy _io.open(self._datfile, 'rb') jako f:
            f.seek(pos)
            dat = f.read(siz)
        zwróć dat

    # Append val to the data file, starting at a _BLOCKSIZE-aligned
    # offset.  The data file jest first padded przy NUL bytes (jeżeli needed)
    # to get to an aligned offset.  Return pair
    #     (starting offset of val, len(val))
    def _addval(self, val):
        przy _io.open(self._datfile, 'rb+') jako f:
            f.seek(0, 2)
            pos = int(f.tell())
            npos = ((pos + _BLOCKSIZE - 1) // _BLOCKSIZE) * _BLOCKSIZE
            f.write(b'\0'*(npos-pos))
            pos = npos
            f.write(val)
        zwróć (pos, len(val))

    # Write val to the data file, starting at offset pos.  The caller
    # jest responsible dla ensuring that there's enough room starting at
    # pos to hold val, without overwriting some other value.  Return
    # pair (pos, len(val)).
    def _setval(self, pos, val):
        przy _io.open(self._datfile, 'rb+') jako f:
            f.seek(pos)
            f.write(val)
        zwróć (pos, len(val))

    # key jest a new key whose associated value starts w the data file
    # at offset pos oraz przy length siz.  Add an index record to
    # the in-memory index dict, oraz append one to the directory file.
    def _addkey(self, key, pos_and_siz_pair):
        self._index[key] = pos_and_siz_pair
        przy _io.open(self._dirfile, 'a', encoding="Latin-1") jako f:
            self._chmod(self._dirfile)
            f.write("%r, %r\n" % (key.decode("Latin-1"), pos_and_siz_pair))

    def __setitem__(self, key, val):
        jeżeli isinstance(key, str):
            key = key.encode('utf-8')
        albo_inaczej nie isinstance(key, (bytes, bytearray)):
            podnieś TypeError("keys must be bytes albo strings")
        jeżeli isinstance(val, str):
            val = val.encode('utf-8')
        albo_inaczej nie isinstance(val, (bytes, bytearray)):
            podnieś TypeError("values must be bytes albo strings")
        self._verify_open()
        jeżeli key nie w self._index:
            self._addkey(key, self._addval(val))
        inaczej:
            # See whether the new value jest small enough to fit w the
            # (padded) space currently occupied by the old value.
            pos, siz = self._index[key]
            oldblocks = (siz + _BLOCKSIZE - 1) // _BLOCKSIZE
            newblocks = (len(val) + _BLOCKSIZE - 1) // _BLOCKSIZE
            jeżeli newblocks <= oldblocks:
                self._index[key] = self._setval(pos, val)
            inaczej:
                # The new value doesn't fit w the (padded) space used
                # by the old value.  The blocks used by the old value are
                # forever lost.
                self._index[key] = self._addval(val)

            # Note that _index may be out of synch przy the directory
            # file now:  _setval() oraz _addval() don't update the directory
            # file.  This also means that the on-disk directory oraz data
            # files are w a mutually inconsistent state, oraz they'll
            # remain that way until _commit() jest called.  Note that this
            # jest a disaster (dla the database) jeżeli the program crashes
            # (so that _commit() never gets called).

    def __delitem__(self, key):
        jeżeli isinstance(key, str):
            key = key.encode('utf-8')
        self._verify_open()
        # The blocks used by the associated value are lost.
        usuń self._index[key]
        # XXX It's unclear why we do a _commit() here (the code always
        # XXX has, so I'm nie changing it).  __setitem__ doesn't try to
        # XXX keep the directory file w synch.  Why should we?  Or
        # XXX why shouldn't __setitem__?
        self._commit()

    def keys(self):
        spróbuj:
            zwróć list(self._index)
        wyjąwszy TypeError:
            podnieś error('DBM object has already been closed') z Nic

    def items(self):
        self._verify_open()
        zwróć [(key, self[key]) dla key w self._index.keys()]

    def __contains__(self, key):
        jeżeli isinstance(key, str):
            key = key.encode('utf-8')
        spróbuj:
            zwróć key w self._index
        wyjąwszy TypeError:
            jeżeli self._index jest Nic:
                podnieś error('DBM object has already been closed') z Nic
            inaczej:
                podnieś

    def iterkeys(self):
        spróbuj:
            zwróć iter(self._index)
        wyjąwszy TypeError:
            podnieś error('DBM object has already been closed') z Nic
    __iter__ = iterkeys

    def __len__(self):
        spróbuj:
            zwróć len(self._index)
        wyjąwszy TypeError:
            podnieś error('DBM object has already been closed') z Nic

    def close(self):
        spróbuj:
            self._commit()
        w_końcu:
            self._index = self._datfile = self._dirfile = self._bakfile = Nic

    __del__ = close

    def _chmod(self, file):
        jeżeli hasattr(self._os, 'chmod'):
            self._os.chmod(file, self._mode)

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.close()


def open(file, flag='c', mode=0o666):
    """Open the database file, filename, oraz zwróć corresponding object.

    The flag argument, used to control how the database jest opened w the
    other DBM implementations, supports only the semantics of 'c' oraz 'n'
    values.  Other values will default to the semantics of 'c' value:
    the database will always opened dla update oraz will be created jeżeli it
    does nie exist.

    The optional mode argument jest the UNIX mode of the file, used only when
    the database has to be created.  It defaults to octal code 0o666 (and
    will be modified by the prevailing umask).

    """

    # Modify mode depending on the umask
    spróbuj:
        um = _os.umask(0)
        _os.umask(um)
    wyjąwszy AttributeError:
        dalej
    inaczej:
        # Turn off any bits that are set w the umask
        mode = mode & (~um)
    zwróć _Database(file, mode, flag=flag)
