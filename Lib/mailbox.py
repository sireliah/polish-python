"""Read/write support dla Maildir, mbox, MH, Babyl, oraz MMDF mailboxes."""

# Notes dla authors of new mailbox subclasses:
#
# Remember to fsync() changes to disk before closing a modified file
# albo returning z a flush() method.  See functions _sync_flush() oraz
# _sync_close().

zaimportuj os
zaimportuj time
zaimportuj calendar
zaimportuj socket
zaimportuj errno
zaimportuj copy
zaimportuj warnings
zaimportuj email
zaimportuj email.message
zaimportuj email.generator
zaimportuj io
zaimportuj contextlib
spróbuj:
    zaimportuj fcntl
wyjąwszy ImportError:
    fcntl = Nic

__all__ = [ 'Mailbox', 'Maildir', 'mbox', 'MH', 'Babyl', 'MMDF',
            'Message', 'MaildirMessage', 'mboxMessage', 'MHMessage',
            'BabylMessage', 'MMDFMessage']

linesep = os.linesep.encode('ascii')

klasa Mailbox:
    """A group of messages w a particular place."""

    def __init__(self, path, factory=Nic, create=Prawda):
        """Initialize a Mailbox instance."""
        self._path = os.path.abspath(os.path.expanduser(path))
        self._factory = factory

    def add(self, message):
        """Add message oraz zwróć assigned key."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def remove(self, key):
        """Remove the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def __delitem__(self, key):
        self.remove(key)

    def discard(self, key):
        """If the keyed message exists, remove it."""
        spróbuj:
            self.remove(key)
        wyjąwszy KeyError:
            dalej

    def __setitem__(self, key, message):
        """Replace the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def get(self, key, default=Nic):
        """Return the keyed message, albo default jeżeli it doesn't exist."""
        spróbuj:
            zwróć self.__getitem__(key)
        wyjąwszy KeyError:
            zwróć default

    def __getitem__(self, key):
        """Return the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        jeżeli nie self._factory:
            zwróć self.get_message(key)
        inaczej:
            przy contextlib.closing(self.get_file(key)) jako file:
                zwróć self._factory(file)

    def get_message(self, key):
        """Return a Message representation albo podnieś a KeyError."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def get_string(self, key):
        """Return a string representation albo podnieś a KeyError.

        Uses email.message.Message to create a 7bit clean string
        representation of the message."""
        zwróć email.message_from_bytes(self.get_bytes(key)).as_string()

    def get_bytes(self, key):
        """Return a byte string representation albo podnieś a KeyError."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def get_file(self, key):
        """Return a file-like representation albo podnieś a KeyError."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def iterkeys(self):
        """Return an iterator over keys."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def keys(self):
        """Return a list of keys."""
        zwróć list(self.iterkeys())

    def itervalues(self):
        """Return an iterator over all messages."""
        dla key w self.iterkeys():
            spróbuj:
                value = self[key]
            wyjąwszy KeyError:
                kontynuuj
            uzyskaj value

    def __iter__(self):
        zwróć self.itervalues()

    def values(self):
        """Return a list of messages. Memory intensive."""
        zwróć list(self.itervalues())

    def iteritems(self):
        """Return an iterator over (key, message) tuples."""
        dla key w self.iterkeys():
            spróbuj:
                value = self[key]
            wyjąwszy KeyError:
                kontynuuj
            uzyskaj (key, value)

    def items(self):
        """Return a list of (key, message) tuples. Memory intensive."""
        zwróć list(self.iteritems())

    def __contains__(self, key):
        """Return Prawda jeżeli the keyed message exists, Nieprawda otherwise."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def __len__(self):
        """Return a count of messages w the mailbox."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def clear(self):
        """Delete all messages."""
        dla key w self.keys():
            self.discard(key)

    def pop(self, key, default=Nic):
        """Delete the keyed message oraz zwróć it, albo default."""
        spróbuj:
            result = self[key]
        wyjąwszy KeyError:
            zwróć default
        self.discard(key)
        zwróć result

    def popitem(self):
        """Delete an arbitrary (key, message) pair oraz zwróć it."""
        dla key w self.iterkeys():
            zwróć (key, self.pop(key))     # This jest only run once.
        inaczej:
            podnieś KeyError('No messages w mailbox')

    def update(self, arg=Nic):
        """Change the messages that correspond to certain keys."""
        jeżeli hasattr(arg, 'iteritems'):
            source = arg.iteritems()
        albo_inaczej hasattr(arg, 'items'):
            source = arg.items()
        inaczej:
            source = arg
        bad_key = Nieprawda
        dla key, message w source:
            spróbuj:
                self[key] = message
            wyjąwszy KeyError:
                bad_key = Prawda
        jeżeli bad_key:
            podnieś KeyError('No message przy key(s)')

    def flush(self):
        """Write any pending changes to the disk."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def lock(self):
        """Lock the mailbox."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def unlock(self):
        """Unlock the mailbox jeżeli it jest locked."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def close(self):
        """Flush oraz close the mailbox."""
        podnieś NotImplementedError('Method must be implemented by subclass')

    def _string_to_bytes(self, message):
        # If a message jest nie 7bit clean, we refuse to handle it since it
        # likely came z reading invalid messages w text mode, oraz that way
        # lies mojibake.
        spróbuj:
            zwróć message.encode('ascii')
        wyjąwszy UnicodeError:
            podnieś ValueError("String input must be ASCII-only; "
                "use bytes albo a Message instead")

    # Whether each message must end w a newline
    _append_newline = Nieprawda

    def _dump_message(self, message, target, mangle_from_=Nieprawda):
        # This assumes the target file jest open w binary mode.
        """Dump message contents to target file."""
        jeżeli isinstance(message, email.message.Message):
            buffer = io.BytesIO()
            gen = email.generator.BytesGenerator(buffer, mangle_from_, 0)
            gen.flatten(message)
            buffer.seek(0)
            data = buffer.read()
            data = data.replace(b'\n', linesep)
            target.write(data)
            jeżeli self._append_newline oraz nie data.endswith(linesep):
                # Make sure the message ends przy a newline
                target.write(linesep)
        albo_inaczej isinstance(message, (str, bytes, io.StringIO)):
            jeżeli isinstance(message, io.StringIO):
                warnings.warn("Use of StringIO input jest deprecated, "
                    "use BytesIO instead", DeprecationWarning, 3)
                message = message.getvalue()
            jeżeli isinstance(message, str):
                message = self._string_to_bytes(message)
            jeżeli mangle_from_:
                message = message.replace(b'\nFrom ', b'\n>From ')
            message = message.replace(b'\n', linesep)
            target.write(message)
            jeżeli self._append_newline oraz nie message.endswith(linesep):
                # Make sure the message ends przy a newline
                target.write(linesep)
        albo_inaczej hasattr(message, 'read'):
            jeżeli hasattr(message, 'buffer'):
                warnings.warn("Use of text mode files jest deprecated, "
                    "use a binary mode file instead", DeprecationWarning, 3)
                message = message.buffer
            lastline = Nic
            dopóki Prawda:
                line = message.readline()
                # Universal newline support.
                jeżeli line.endswith(b'\r\n'):
                    line = line[:-2] + b'\n'
                albo_inaczej line.endswith(b'\r'):
                    line = line[:-1] + b'\n'
                jeżeli nie line:
                    przerwij
                jeżeli mangle_from_ oraz line.startswith(b'From '):
                    line = b'>From ' + line[5:]
                line = line.replace(b'\n', linesep)
                target.write(line)
                lastline = line
            jeżeli self._append_newline oraz lastline oraz nie lastline.endswith(linesep):
                # Make sure the message ends przy a newline
                target.write(linesep)
        inaczej:
            podnieś TypeError('Invalid message type: %s' % type(message))


klasa Maildir(Mailbox):
    """A qmail-style Maildir mailbox."""

    colon = ':'

    def __init__(self, dirname, factory=Nic, create=Prawda):
        """Initialize a Maildir instance."""
        Mailbox.__init__(self, dirname, factory, create)
        self._paths = {
            'tmp': os.path.join(self._path, 'tmp'),
            'new': os.path.join(self._path, 'new'),
            'cur': os.path.join(self._path, 'cur'),
            }
        jeżeli nie os.path.exists(self._path):
            jeżeli create:
                os.mkdir(self._path, 0o700)
                dla path w self._paths.values():
                    os.mkdir(path, 0o700)
            inaczej:
                podnieś NoSuchMailboxError(self._path)
        self._toc = {}
        self._toc_mtimes = {'cur': 0, 'new': 0}
        self._last_read = 0         # Records last time we read cur/new
        self._skewfactor = 0.1      # Adjust jeżeli os/fs clocks are skewing

    def add(self, message):
        """Add message oraz zwróć assigned key."""
        tmp_file = self._create_tmp()
        spróbuj:
            self._dump_message(message, tmp_file)
        wyjąwszy BaseException:
            tmp_file.close()
            os.remove(tmp_file.name)
            podnieś
        _sync_close(tmp_file)
        jeżeli isinstance(message, MaildirMessage):
            subdir = message.get_subdir()
            suffix = self.colon + message.get_info()
            jeżeli suffix == self.colon:
                suffix = ''
        inaczej:
            subdir = 'new'
            suffix = ''
        uniq = os.path.basename(tmp_file.name).split(self.colon)[0]
        dest = os.path.join(self._path, subdir, uniq + suffix)
        jeżeli isinstance(message, MaildirMessage):
            os.utime(tmp_file.name,
                     (os.path.getatime(tmp_file.name), message.get_date()))
        # No file modification should be done after the file jest moved to its
        # final position w order to prevent race conditions przy changes
        # z other programs
        spróbuj:
            jeżeli hasattr(os, 'link'):
                os.link(tmp_file.name, dest)
                os.remove(tmp_file.name)
            inaczej:
                os.rename(tmp_file.name, dest)
        wyjąwszy OSError jako e:
            os.remove(tmp_file.name)
            jeżeli e.errno == errno.EEXIST:
                podnieś ExternalClashError('Name clash przy existing message: %s'
                                         % dest)
            inaczej:
                podnieś
        zwróć uniq

    def remove(self, key):
        """Remove the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        os.remove(os.path.join(self._path, self._lookup(key)))

    def discard(self, key):
        """If the keyed message exists, remove it."""
        # This overrides an inapplicable implementation w the superclass.
        spróbuj:
            self.remove(key)
        wyjąwszy (KeyError, FileNotFoundError):
            dalej

    def __setitem__(self, key, message):
        """Replace the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        old_subpath = self._lookup(key)
        temp_key = self.add(message)
        temp_subpath = self._lookup(temp_key)
        jeżeli isinstance(message, MaildirMessage):
            # temp's subdir oraz suffix were specified by message.
            dominant_subpath = temp_subpath
        inaczej:
            # temp's subdir oraz suffix were defaults z add().
            dominant_subpath = old_subpath
        subdir = os.path.dirname(dominant_subpath)
        jeżeli self.colon w dominant_subpath:
            suffix = self.colon + dominant_subpath.split(self.colon)[-1]
        inaczej:
            suffix = ''
        self.discard(key)
        tmp_path = os.path.join(self._path, temp_subpath)
        new_path = os.path.join(self._path, subdir, key + suffix)
        jeżeli isinstance(message, MaildirMessage):
            os.utime(tmp_path,
                     (os.path.getatime(tmp_path), message.get_date()))
        # No file modification should be done after the file jest moved to its
        # final position w order to prevent race conditions przy changes
        # z other programs
        os.rename(tmp_path, new_path)

    def get_message(self, key):
        """Return a Message representation albo podnieś a KeyError."""
        subpath = self._lookup(key)
        przy open(os.path.join(self._path, subpath), 'rb') jako f:
            jeżeli self._factory:
                msg = self._factory(f)
            inaczej:
                msg = MaildirMessage(f)
        subdir, name = os.path.split(subpath)
        msg.set_subdir(subdir)
        jeżeli self.colon w name:
            msg.set_info(name.split(self.colon)[-1])
        msg.set_date(os.path.getmtime(os.path.join(self._path, subpath)))
        zwróć msg

    def get_bytes(self, key):
        """Return a bytes representation albo podnieś a KeyError."""
        przy open(os.path.join(self._path, self._lookup(key)), 'rb') jako f:
            zwróć f.read().replace(linesep, b'\n')

    def get_file(self, key):
        """Return a file-like representation albo podnieś a KeyError."""
        f = open(os.path.join(self._path, self._lookup(key)), 'rb')
        zwróć _ProxyFile(f)

    def iterkeys(self):
        """Return an iterator over keys."""
        self._refresh()
        dla key w self._toc:
            spróbuj:
                self._lookup(key)
            wyjąwszy KeyError:
                kontynuuj
            uzyskaj key

    def __contains__(self, key):
        """Return Prawda jeżeli the keyed message exists, Nieprawda otherwise."""
        self._refresh()
        zwróć key w self._toc

    def __len__(self):
        """Return a count of messages w the mailbox."""
        self._refresh()
        zwróć len(self._toc)

    def flush(self):
        """Write any pending changes to disk."""
        # Maildir changes are always written immediately, so there's nothing
        # to do.
        dalej

    def lock(self):
        """Lock the mailbox."""
        zwróć

    def unlock(self):
        """Unlock the mailbox jeżeli it jest locked."""
        zwróć

    def close(self):
        """Flush oraz close the mailbox."""
        zwróć

    def list_folders(self):
        """Return a list of folder names."""
        result = []
        dla entry w os.listdir(self._path):
            jeżeli len(entry) > 1 oraz entry[0] == '.' oraz \
               os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry[1:])
        zwróć result

    def get_folder(self, folder):
        """Return a Maildir instance dla the named folder."""
        zwróć Maildir(os.path.join(self._path, '.' + folder),
                       factory=self._factory,
                       create=Nieprawda)

    def add_folder(self, folder):
        """Create a folder oraz zwróć a Maildir instance representing it."""
        path = os.path.join(self._path, '.' + folder)
        result = Maildir(path, factory=self._factory)
        maildirfolder_path = os.path.join(path, 'maildirfolder')
        jeżeli nie os.path.exists(maildirfolder_path):
            os.close(os.open(maildirfolder_path, os.O_CREAT | os.O_WRONLY,
                0o666))
        zwróć result

    def remove_folder(self, folder):
        """Delete the named folder, which must be empty."""
        path = os.path.join(self._path, '.' + folder)
        dla entry w os.listdir(os.path.join(path, 'new')) + \
                     os.listdir(os.path.join(path, 'cur')):
            jeżeli len(entry) < 1 albo entry[0] != '.':
                podnieś NotEmptyError('Folder contains message(s): %s' % folder)
        dla entry w os.listdir(path):
            jeżeli entry != 'new' oraz entry != 'cur' oraz entry != 'tmp' oraz \
               os.path.isdir(os.path.join(path, entry)):
                podnieś NotEmptyError("Folder contains subdirectory '%s': %s" %
                                    (folder, entry))
        dla root, dirs, files w os.walk(path, topdown=Nieprawda):
            dla entry w files:
                os.remove(os.path.join(root, entry))
            dla entry w dirs:
                os.rmdir(os.path.join(root, entry))
        os.rmdir(path)

    def clean(self):
        """Delete old files w "tmp"."""
        now = time.time()
        dla entry w os.listdir(os.path.join(self._path, 'tmp')):
            path = os.path.join(self._path, 'tmp', entry)
            jeżeli now - os.path.getatime(path) > 129600:   # 60 * 60 * 36
                os.remove(path)

    _count = 1  # This jest used to generate unique file names.

    def _create_tmp(self):
        """Create a file w the tmp subdirectory oraz open oraz zwróć it."""
        now = time.time()
        hostname = socket.gethostname()
        jeżeli '/' w hostname:
            hostname = hostname.replace('/', r'\057')
        jeżeli ':' w hostname:
            hostname = hostname.replace(':', r'\072')
        uniq = "%s.M%sP%sQ%s.%s" % (int(now), int(now % 1 * 1e6), os.getpid(),
                                    Maildir._count, hostname)
        path = os.path.join(self._path, 'tmp', uniq)
        spróbuj:
            os.stat(path)
        wyjąwszy FileNotFoundError:
            Maildir._count += 1
            spróbuj:
                zwróć _create_carefully(path)
            wyjąwszy FileExistsError:
                dalej

        # Fall through to here jeżeli stat succeeded albo open podnieśd EEXIST.
        podnieś ExternalClashError('Name clash prevented file creation: %s' %
                                 path)

    def _refresh(self):
        """Update table of contents mapping."""
        # If it has been less than two seconds since the last _refresh() call,
        # we have to unconditionally re-read the mailbox just w case it has
        # been modified, because os.path.mtime() has a 2 sec resolution w the
        # most common worst case (FAT) oraz a 1 sec resolution typically.  This
        # results w a few unnecessary re-reads when _refresh() jest called
        # multiple times w that interval, but once the clock ticks over, we
        # will only re-read jako needed.  Because the filesystem might be being
        # served by an independent system przy its own clock, we record oraz
        # compare przy the mtimes z the filesystem.  Because the other
        # system's clock might be skewing relative to our clock, we add an
        # extra delta to our wait.  The default jest one tenth second, but jest an
        # instance variable oraz so can be adjusted jeżeli dealing przy a
        # particularly skewed albo irregular system.
        jeżeli time.time() - self._last_read > 2 + self._skewfactor:
            refresh = Nieprawda
            dla subdir w self._toc_mtimes:
                mtime = os.path.getmtime(self._paths[subdir])
                jeżeli mtime > self._toc_mtimes[subdir]:
                    refresh = Prawda
                self._toc_mtimes[subdir] = mtime
            jeżeli nie refresh:
                zwróć
        # Refresh toc
        self._toc = {}
        dla subdir w self._toc_mtimes:
            path = self._paths[subdir]
            dla entry w os.listdir(path):
                p = os.path.join(path, entry)
                jeżeli os.path.isdir(p):
                    kontynuuj
                uniq = entry.split(self.colon)[0]
                self._toc[uniq] = os.path.join(subdir, entry)
        self._last_read = time.time()

    def _lookup(self, key):
        """Use TOC to zwróć subpath dla given key, albo podnieś a KeyError."""
        spróbuj:
            jeżeli os.path.exists(os.path.join(self._path, self._toc[key])):
                zwróć self._toc[key]
        wyjąwszy KeyError:
            dalej
        self._refresh()
        spróbuj:
            zwróć self._toc[key]
        wyjąwszy KeyError:
            podnieś KeyError('No message przy key: %s' % key)

    # This method jest dla backward compatibility only.
    def next(self):
        """Return the next message w a one-time iteration."""
        jeżeli nie hasattr(self, '_onetime_keys'):
            self._onetime_keys = self.iterkeys()
        dopóki Prawda:
            spróbuj:
                zwróć self[next(self._onetime_keys)]
            wyjąwszy StopIteration:
                zwróć Nic
            wyjąwszy KeyError:
                kontynuuj


klasa _singlefileMailbox(Mailbox):
    """A single-file mailbox."""

    def __init__(self, path, factory=Nic, create=Prawda):
        """Initialize a single-file mailbox."""
        Mailbox.__init__(self, path, factory, create)
        spróbuj:
            f = open(self._path, 'rb+')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.ENOENT:
                jeżeli create:
                    f = open(self._path, 'wb+')
                inaczej:
                    podnieś NoSuchMailboxError(self._path)
            albo_inaczej e.errno w (errno.EACCES, errno.EROFS):
                f = open(self._path, 'rb')
            inaczej:
                podnieś
        self._file = f
        self._toc = Nic
        self._next_key = 0
        self._pending = Nieprawda       # No changes require rewriting the file.
        self._pending_sync = Nieprawda  # No need to sync the file
        self._locked = Nieprawda
        self._file_length = Nic    # Used to record mailbox size

    def add(self, message):
        """Add message oraz zwróć assigned key."""
        self._lookup()
        self._toc[self._next_key] = self._append_message(message)
        self._next_key += 1
        # _append_message appends the message to the mailbox file. We
        # don't need a full rewrite + rename, sync jest enough.
        self._pending_sync = Prawda
        zwróć self._next_key - 1

    def remove(self, key):
        """Remove the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        self._lookup(key)
        usuń self._toc[key]
        self._pending = Prawda

    def __setitem__(self, key, message):
        """Replace the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        self._lookup(key)
        self._toc[key] = self._append_message(message)
        self._pending = Prawda

    def iterkeys(self):
        """Return an iterator over keys."""
        self._lookup()
        uzyskaj z self._toc.keys()

    def __contains__(self, key):
        """Return Prawda jeżeli the keyed message exists, Nieprawda otherwise."""
        self._lookup()
        zwróć key w self._toc

    def __len__(self):
        """Return a count of messages w the mailbox."""
        self._lookup()
        zwróć len(self._toc)

    def lock(self):
        """Lock the mailbox."""
        jeżeli nie self._locked:
            _lock_file(self._file)
            self._locked = Prawda

    def unlock(self):
        """Unlock the mailbox jeżeli it jest locked."""
        jeżeli self._locked:
            _unlock_file(self._file)
            self._locked = Nieprawda

    def flush(self):
        """Write any pending changes to disk."""
        jeżeli nie self._pending:
            jeżeli self._pending_sync:
                # Messages have only been added, so syncing the file
                # jest enough.
                _sync_flush(self._file)
                self._pending_sync = Nieprawda
            zwróć

        # In order to be writing anything out at all, self._toc must
        # already have been generated (and presumably has been modified
        # by adding albo deleting an item).
        assert self._toc jest nie Nic

        # Check length of self._file; jeżeli it's changed, some other process
        # has modified the mailbox since we scanned it.
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        jeżeli cur_len != self._file_length:
            podnieś ExternalClashError('Size of mailbox file changed '
                                     '(expected %i, found %i)' %
                                     (self._file_length, cur_len))

        new_file = _create_temporary(self._path)
        spróbuj:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            dla key w sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                dopóki Prawda:
                    buffer = self._file.read(min(4096,
                                                 stop - self._file.tell()))
                    jeżeli nie buffer:
                        przerwij
                    new_file.write(buffer)
                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)
            self._file_length = new_file.tell()
        wyjąwszy:
            new_file.close()
            os.remove(new_file.name)
            podnieś
        _sync_close(new_file)
        # self._file jest about to get replaced, so no need to sync.
        self._file.close()
        # Make sure the new file's mode jest the same jako the old file's
        mode = os.stat(self._path).st_mode
        os.chmod(new_file.name, mode)
        spróbuj:
            os.rename(new_file.name, self._path)
        wyjąwszy FileExistsError:
            os.remove(self._path)
            os.rename(new_file.name, self._path)
        self._file = open(self._path, 'rb+')
        self._toc = new_toc
        self._pending = Nieprawda
        self._pending_sync = Nieprawda
        jeżeli self._locked:
            _lock_file(self._file, dotlock=Nieprawda)

    def _pre_mailbox_hook(self, f):
        """Called before writing the mailbox to file f."""
        zwróć

    def _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        zwróć

    def _post_message_hook(self, f):
        """Called after writing each message to file f."""
        zwróć

    def close(self):
        """Flush oraz close the mailbox."""
        spróbuj:
            self.flush()
        w_końcu:
            spróbuj:
                jeżeli self._locked:
                    self.unlock()
            w_końcu:
                self._file.close()  # Sync has been done by self.flush() above.

    def _lookup(self, key=Nic):
        """Return (start, stop) albo podnieś KeyError."""
        jeżeli self._toc jest Nic:
            self._generate_toc()
        jeżeli key jest nie Nic:
            spróbuj:
                zwróć self._toc[key]
            wyjąwszy KeyError:
                podnieś KeyError('No message przy key: %s' % key)

    def _append_message(self, message):
        """Append message to mailbox oraz zwróć (start, stop) offsets."""
        self._file.seek(0, 2)
        before = self._file.tell()
        jeżeli len(self._toc) == 0 oraz nie self._pending:
            # This jest the first message, oraz the _pre_mailbox_hook
            # hasn't yet been called. If self._pending jest Prawda,
            # messages have been removed, so _pre_mailbox_hook must
            # have been called already.
            self._pre_mailbox_hook(self._file)
        spróbuj:
            self._pre_message_hook(self._file)
            offsets = self._install_message(message)
            self._post_message_hook(self._file)
        wyjąwszy BaseException:
            self._file.truncate(before)
            podnieś
        self._file.flush()
        self._file_length = self._file.tell()  # Record current length of mailbox
        zwróć offsets



klasa _mboxMMDF(_singlefileMailbox):
    """An mbox albo MMDF mailbox."""

    _mangle_from_ = Prawda

    def get_message(self, key):
        """Return a Message representation albo podnieś a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        from_line = self._file.readline().replace(linesep, b'')
        string = self._file.read(stop - self._file.tell())
        msg = self._message_factory(string.replace(linesep, b'\n'))
        msg.set_from(from_line[5:].decode('ascii'))
        zwróć msg

    def get_string(self, key, from_=Nieprawda):
        """Return a string representation albo podnieś a KeyError."""
        zwróć email.message_from_bytes(
            self.get_bytes(key)).as_string(unixfrom=from_)

    def get_bytes(self, key, from_=Nieprawda):
        """Return a string representation albo podnieś a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        jeżeli nie from_:
            self._file.readline()
        string = self._file.read(stop - self._file.tell())
        zwróć string.replace(linesep, b'\n')

    def get_file(self, key, from_=Nieprawda):
        """Return a file-like representation albo podnieś a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        jeżeli nie from_:
            self._file.readline()
        zwróć _PartialFile(self._file, self._file.tell(), stop)

    def _install_message(self, message):
        """Format a message oraz blindly write to self._file."""
        from_line = Nic
        jeżeli isinstance(message, str):
            message = self._string_to_bytes(message)
        jeżeli isinstance(message, bytes) oraz message.startswith(b'From '):
            newline = message.find(b'\n')
            jeżeli newline != -1:
                from_line = message[:newline]
                message = message[newline + 1:]
            inaczej:
                from_line = message
                message = b''
        albo_inaczej isinstance(message, _mboxMMDFMessage):
            author = message.get_from().encode('ascii')
            from_line = b'From ' + author
        albo_inaczej isinstance(message, email.message.Message):
            from_line = message.get_unixfrom()  # May be Nic.
            jeżeli from_line jest nie Nic:
                from_line = from_line.encode('ascii')
        jeżeli from_line jest Nic:
            from_line = b'From MAILER-DAEMON ' + time.asctime(time.gmtime()).encode()
        start = self._file.tell()
        self._file.write(from_line + linesep)
        self._dump_message(message, self._file, self._mangle_from_)
        stop = self._file.tell()
        zwróć (start, stop)


klasa mbox(_mboxMMDF):
    """A classic mbox mailbox."""

    _mangle_from_ = Prawda

    # All messages must end w a newline character, oraz
    # _post_message_hooks outputs an empty line between messages.
    _append_newline = Prawda

    def __init__(self, path, factory=Nic, create=Prawda):
        """Initialize an mbox mailbox."""
        self._message_factory = mboxMessage
        _mboxMMDF.__init__(self, path, factory, create)

    def _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep)

    def _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        last_was_empty = Nieprawda
        self._file.seek(0)
        dopóki Prawda:
            line_pos = self._file.tell()
            line = self._file.readline()
            jeżeli line.startswith(b'From '):
                jeżeli len(stops) < len(starts):
                    jeżeli last_was_empty:
                        stops.append(line_pos - len(linesep))
                    inaczej:
                        # The last line before the "From " line wasn't
                        # blank, but we consider it a start of a
                        # message anyway.
                        stops.append(line_pos)
                starts.append(line_pos)
                last_was_empty = Nieprawda
            albo_inaczej nie line:
                jeżeli last_was_empty:
                    stops.append(line_pos - len(linesep))
                inaczej:
                    stops.append(line_pos)
                przerwij
            albo_inaczej line == linesep:
                last_was_empty = Prawda
            inaczej:
                last_was_empty = Nieprawda
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()


klasa MMDF(_mboxMMDF):
    """An MMDF mailbox."""

    def __init__(self, path, factory=Nic, create=Prawda):
        """Initialize an MMDF mailbox."""
        self._message_factory = MMDFMessage
        _mboxMMDF.__init__(self, path, factory, create)

    def _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        f.write(b'\001\001\001\001' + linesep)

    def _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep + b'\001\001\001\001' + linesep)

    def _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        dopóki Prawda:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            jeżeli line.startswith(b'\001\001\001\001' + linesep):
                starts.append(next_pos)
                dopóki Prawda:
                    line_pos = next_pos
                    line = self._file.readline()
                    next_pos = self._file.tell()
                    jeżeli line == b'\001\001\001\001' + linesep:
                        stops.append(line_pos - len(linesep))
                        przerwij
                    albo_inaczej nie line:
                        stops.append(line_pos)
                        przerwij
            albo_inaczej nie line:
                przerwij
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()


klasa MH(Mailbox):
    """An MH mailbox."""

    def __init__(self, path, factory=Nic, create=Prawda):
        """Initialize an MH instance."""
        Mailbox.__init__(self, path, factory, create)
        jeżeli nie os.path.exists(self._path):
            jeżeli create:
                os.mkdir(self._path, 0o700)
                os.close(os.open(os.path.join(self._path, '.mh_sequences'),
                                 os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
            inaczej:
                podnieś NoSuchMailboxError(self._path)
        self._locked = Nieprawda

    def add(self, message):
        """Add message oraz zwróć assigned key."""
        keys = self.keys()
        jeżeli len(keys) == 0:
            new_key = 1
        inaczej:
            new_key = max(keys) + 1
        new_path = os.path.join(self._path, str(new_key))
        f = _create_carefully(new_path)
        closed = Nieprawda
        spróbuj:
            jeżeli self._locked:
                _lock_file(f)
            spróbuj:
                spróbuj:
                    self._dump_message(message, f)
                wyjąwszy BaseException:
                    # Unlock oraz close so it can be deleted on Windows
                    jeżeli self._locked:
                        _unlock_file(f)
                    _sync_close(f)
                    closed = Prawda
                    os.remove(new_path)
                    podnieś
                jeżeli isinstance(message, MHMessage):
                    self._dump_sequences(message, new_key)
            w_końcu:
                jeżeli self._locked:
                    _unlock_file(f)
        w_końcu:
            jeżeli nie closed:
                _sync_close(f)
        zwróć new_key

    def remove(self, key):
        """Remove the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        path = os.path.join(self._path, str(key))
        spróbuj:
            f = open(path, 'rb+')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.ENOENT:
                podnieś KeyError('No message przy key: %s' % key)
            inaczej:
                podnieś
        inaczej:
            f.close()
            os.remove(path)

    def __setitem__(self, key, message):
        """Replace the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        path = os.path.join(self._path, str(key))
        spróbuj:
            f = open(path, 'rb+')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.ENOENT:
                podnieś KeyError('No message przy key: %s' % key)
            inaczej:
                podnieś
        spróbuj:
            jeżeli self._locked:
                _lock_file(f)
            spróbuj:
                os.close(os.open(path, os.O_WRONLY | os.O_TRUNC))
                self._dump_message(message, f)
                jeżeli isinstance(message, MHMessage):
                    self._dump_sequences(message, key)
            w_końcu:
                jeżeli self._locked:
                    _unlock_file(f)
        w_końcu:
            _sync_close(f)

    def get_message(self, key):
        """Return a Message representation albo podnieś a KeyError."""
        spróbuj:
            jeżeli self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            inaczej:
                f = open(os.path.join(self._path, str(key)), 'rb')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.ENOENT:
                podnieś KeyError('No message przy key: %s' % key)
            inaczej:
                podnieś
        przy f:
            jeżeli self._locked:
                _lock_file(f)
            spróbuj:
                msg = MHMessage(f)
            w_końcu:
                jeżeli self._locked:
                    _unlock_file(f)
        dla name, key_list w self.get_sequences().items():
            jeżeli key w key_list:
                msg.add_sequence(name)
        zwróć msg

    def get_bytes(self, key):
        """Return a bytes representation albo podnieś a KeyError."""
        spróbuj:
            jeżeli self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            inaczej:
                f = open(os.path.join(self._path, str(key)), 'rb')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.ENOENT:
                podnieś KeyError('No message przy key: %s' % key)
            inaczej:
                podnieś
        przy f:
            jeżeli self._locked:
                _lock_file(f)
            spróbuj:
                zwróć f.read().replace(linesep, b'\n')
            w_końcu:
                jeżeli self._locked:
                    _unlock_file(f)

    def get_file(self, key):
        """Return a file-like representation albo podnieś a KeyError."""
        spróbuj:
            f = open(os.path.join(self._path, str(key)), 'rb')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.ENOENT:
                podnieś KeyError('No message przy key: %s' % key)
            inaczej:
                podnieś
        zwróć _ProxyFile(f)

    def iterkeys(self):
        """Return an iterator over keys."""
        zwróć iter(sorted(int(entry) dla entry w os.listdir(self._path)
                                      jeżeli entry.isdigit()))

    def __contains__(self, key):
        """Return Prawda jeżeli the keyed message exists, Nieprawda otherwise."""
        zwróć os.path.exists(os.path.join(self._path, str(key)))

    def __len__(self):
        """Return a count of messages w the mailbox."""
        zwróć len(list(self.iterkeys()))

    def lock(self):
        """Lock the mailbox."""
        jeżeli nie self._locked:
            self._file = open(os.path.join(self._path, '.mh_sequences'), 'rb+')
            _lock_file(self._file)
            self._locked = Prawda

    def unlock(self):
        """Unlock the mailbox jeżeli it jest locked."""
        jeżeli self._locked:
            _unlock_file(self._file)
            _sync_close(self._file)
            usuń self._file
            self._locked = Nieprawda

    def flush(self):
        """Write any pending changes to the disk."""
        zwróć

    def close(self):
        """Flush oraz close the mailbox."""
        jeżeli self._locked:
            self.unlock()

    def list_folders(self):
        """Return a list of folder names."""
        result = []
        dla entry w os.listdir(self._path):
            jeżeli os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry)
        zwróć result

    def get_folder(self, folder):
        """Return an MH instance dla the named folder."""
        zwróć MH(os.path.join(self._path, folder),
                  factory=self._factory, create=Nieprawda)

    def add_folder(self, folder):
        """Create a folder oraz zwróć an MH instance representing it."""
        zwróć MH(os.path.join(self._path, folder),
                  factory=self._factory)

    def remove_folder(self, folder):
        """Delete the named folder, which must be empty."""
        path = os.path.join(self._path, folder)
        entries = os.listdir(path)
        jeżeli entries == ['.mh_sequences']:
            os.remove(os.path.join(path, '.mh_sequences'))
        albo_inaczej entries == []:
            dalej
        inaczej:
            podnieś NotEmptyError('Folder nie empty: %s' % self._path)
        os.rmdir(path)

    def get_sequences(self):
        """Return a name-to-key-list dictionary to define each sequence."""
        results = {}
        przy open(os.path.join(self._path, '.mh_sequences'), 'r', encoding='ASCII') jako f:
            all_keys = set(self.keys())
            dla line w f:
                spróbuj:
                    name, contents = line.split(':')
                    keys = set()
                    dla spec w contents.split():
                        jeżeli spec.isdigit():
                            keys.add(int(spec))
                        inaczej:
                            start, stop = (int(x) dla x w spec.split('-'))
                            keys.update(range(start, stop + 1))
                    results[name] = [key dla key w sorted(keys) \
                                         jeżeli key w all_keys]
                    jeżeli len(results[name]) == 0:
                        usuń results[name]
                wyjąwszy ValueError:
                    podnieś FormatError('Invalid sequence specification: %s' %
                                      line.rstrip())
        zwróć results

    def set_sequences(self, sequences):
        """Set sequences using the given name-to-key-list dictionary."""
        f = open(os.path.join(self._path, '.mh_sequences'), 'r+', encoding='ASCII')
        spróbuj:
            os.close(os.open(f.name, os.O_WRONLY | os.O_TRUNC))
            dla name, keys w sequences.items():
                jeżeli len(keys) == 0:
                    kontynuuj
                f.write(name + ':')
                prev = Nic
                completing = Nieprawda
                dla key w sorted(set(keys)):
                    jeżeli key - 1 == prev:
                        jeżeli nie completing:
                            completing = Prawda
                            f.write('-')
                    albo_inaczej completing:
                        completing = Nieprawda
                        f.write('%s %s' % (prev, key))
                    inaczej:
                        f.write(' %s' % key)
                    prev = key
                jeżeli completing:
                    f.write(str(prev) + '\n')
                inaczej:
                    f.write('\n')
        w_końcu:
            _sync_close(f)

    def pack(self):
        """Re-name messages to eliminate numbering gaps. Invalidates keys."""
        sequences = self.get_sequences()
        prev = 0
        changes = []
        dla key w self.iterkeys():
            jeżeli key - 1 != prev:
                changes.append((key, prev + 1))
                jeżeli hasattr(os, 'link'):
                    os.link(os.path.join(self._path, str(key)),
                            os.path.join(self._path, str(prev + 1)))
                    os.unlink(os.path.join(self._path, str(key)))
                inaczej:
                    os.rename(os.path.join(self._path, str(key)),
                              os.path.join(self._path, str(prev + 1)))
            prev += 1
        self._next_key = prev + 1
        jeżeli len(changes) == 0:
            zwróć
        dla name, key_list w sequences.items():
            dla old, new w changes:
                jeżeli old w key_list:
                    key_list[key_list.index(old)] = new
        self.set_sequences(sequences)

    def _dump_sequences(self, message, key):
        """Inspect a new MHMessage oraz update sequences appropriately."""
        pending_sequences = message.get_sequences()
        all_sequences = self.get_sequences()
        dla name, key_list w all_sequences.items():
            jeżeli name w pending_sequences:
                key_list.append(key)
            albo_inaczej key w key_list:
                usuń key_list[key_list.index(key)]
        dla sequence w pending_sequences:
            jeżeli sequence nie w all_sequences:
                all_sequences[sequence] = [key]
        self.set_sequences(all_sequences)


klasa Babyl(_singlefileMailbox):
    """An Rmail-style Babyl mailbox."""

    _special_labels = frozenset({'unseen', 'deleted', 'filed', 'answered',
                                 'forwarded', 'edited', 'resent'})

    def __init__(self, path, factory=Nic, create=Prawda):
        """Initialize a Babyl mailbox."""
        _singlefileMailbox.__init__(self, path, factory, create)
        self._labels = {}

    def add(self, message):
        """Add message oraz zwróć assigned key."""
        key = _singlefileMailbox.add(self, message)
        jeżeli isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()
        zwróć key

    def remove(self, key):
        """Remove the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        _singlefileMailbox.remove(self, key)
        jeżeli key w self._labels:
            usuń self._labels[key]

    def __setitem__(self, key, message):
        """Replace the keyed message; podnieś KeyError jeżeli it doesn't exist."""
        _singlefileMailbox.__setitem__(self, key, message)
        jeżeli isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()

    def get_message(self, key):
        """Return a Message representation albo podnieś a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()   # Skip b'1,' line specifying labels.
        original_headers = io.BytesIO()
        dopóki Prawda:
            line = self._file.readline()
            jeżeli line == b'*** EOOH ***' + linesep albo nie line:
                przerwij
            original_headers.write(line.replace(linesep, b'\n'))
        visible_headers = io.BytesIO()
        dopóki Prawda:
            line = self._file.readline()
            jeżeli line == linesep albo nie line:
                przerwij
            visible_headers.write(line.replace(linesep, b'\n'))
        # Read up to the stop, albo to the end
        n = stop - self._file.tell()
        assert n >= 0
        body = self._file.read(n)
        body = body.replace(linesep, b'\n')
        msg = BabylMessage(original_headers.getvalue() + body)
        msg.set_visible(visible_headers.getvalue())
        jeżeli key w self._labels:
            msg.set_labels(self._labels[key])
        zwróć msg

    def get_bytes(self, key):
        """Return a string representation albo podnieś a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()   # Skip b'1,' line specifying labels.
        original_headers = io.BytesIO()
        dopóki Prawda:
            line = self._file.readline()
            jeżeli line == b'*** EOOH ***' + linesep albo nie line:
                przerwij
            original_headers.write(line.replace(linesep, b'\n'))
        dopóki Prawda:
            line = self._file.readline()
            jeżeli line == linesep albo nie line:
                przerwij
        headers = original_headers.getvalue()
        n = stop - self._file.tell()
        assert n >= 0
        data = self._file.read(n)
        data = data.replace(linesep, b'\n')
        zwróć headers + data

    def get_file(self, key):
        """Return a file-like representation albo podnieś a KeyError."""
        zwróć io.BytesIO(self.get_bytes(key).replace(b'\n', linesep))

    def get_labels(self):
        """Return a list of user-defined labels w the mailbox."""
        self._lookup()
        labels = set()
        dla label_list w self._labels.values():
            labels.update(label_list)
        labels.difference_update(self._special_labels)
        zwróć list(labels)

    def _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        label_lists = []
        dopóki Prawda:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            jeżeli line == b'\037\014' + linesep:
                jeżeli len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
                starts.append(next_pos)
                labels = [label.strip() dla label
                                        w self._file.readline()[1:].split(b',')
                                        jeżeli label.strip()]
                label_lists.append(labels)
            albo_inaczej line == b'\037' albo line == b'\037' + linesep:
                jeżeli len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
            albo_inaczej nie line:
                stops.append(line_pos - len(linesep))
                przerwij
        self._toc = dict(enumerate(zip(starts, stops)))
        self._labels = dict(enumerate(label_lists))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()

    def _pre_mailbox_hook(self, f):
        """Called before writing the mailbox to file f."""
        babyl = b'BABYL OPTIONS:' + linesep
        babyl += b'Version: 5' + linesep
        labels = self.get_labels()
        labels = (label.encode() dla label w labels)
        babyl += b'Labels:' + b','.join(labels) + linesep
        babyl += b'\037'
        f.write(babyl)

    def _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        f.write(b'\014' + linesep)

    def _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep + b'\037')

    def _install_message(self, message):
        """Write message contents oraz zwróć (start, stop)."""
        start = self._file.tell()
        jeżeli isinstance(message, BabylMessage):
            special_labels = []
            labels = []
            dla label w message.get_labels():
                jeżeli label w self._special_labels:
                    special_labels.append(label)
                inaczej:
                    labels.append(label)
            self._file.write(b'1')
            dla label w special_labels:
                self._file.write(b', ' + label.encode())
            self._file.write(b',,')
            dla label w labels:
                self._file.write(b' ' + label.encode() + b',')
            self._file.write(linesep)
        inaczej:
            self._file.write(b'1,,' + linesep)
        jeżeli isinstance(message, email.message.Message):
            orig_buffer = io.BytesIO()
            orig_generator = email.generator.BytesGenerator(orig_buffer, Nieprawda, 0)
            orig_generator.flatten(message)
            orig_buffer.seek(0)
            dopóki Prawda:
                line = orig_buffer.readline()
                self._file.write(line.replace(b'\n', linesep))
                jeżeli line == b'\n' albo nie line:
                    przerwij
            self._file.write(b'*** EOOH ***' + linesep)
            jeżeli isinstance(message, BabylMessage):
                vis_buffer = io.BytesIO()
                vis_generator = email.generator.BytesGenerator(vis_buffer, Nieprawda, 0)
                vis_generator.flatten(message.get_visible())
                dopóki Prawda:
                    line = vis_buffer.readline()
                    self._file.write(line.replace(b'\n', linesep))
                    jeżeli line == b'\n' albo nie line:
                        przerwij
            inaczej:
                orig_buffer.seek(0)
                dopóki Prawda:
                    line = orig_buffer.readline()
                    self._file.write(line.replace(b'\n', linesep))
                    jeżeli line == b'\n' albo nie line:
                        przerwij
            dopóki Prawda:
                buffer = orig_buffer.read(4096) # Buffer size jest arbitrary.
                jeżeli nie buffer:
                    przerwij
                self._file.write(buffer.replace(b'\n', linesep))
        albo_inaczej isinstance(message, (bytes, str, io.StringIO)):
            jeżeli isinstance(message, io.StringIO):
                warnings.warn("Use of StringIO input jest deprecated, "
                    "use BytesIO instead", DeprecationWarning, 3)
                message = message.getvalue()
            jeżeli isinstance(message, str):
                message = self._string_to_bytes(message)
            body_start = message.find(b'\n\n') + 2
            jeżeli body_start - 2 != -1:
                self._file.write(message[:body_start].replace(b'\n', linesep))
                self._file.write(b'*** EOOH ***' + linesep)
                self._file.write(message[:body_start].replace(b'\n', linesep))
                self._file.write(message[body_start:].replace(b'\n', linesep))
            inaczej:
                self._file.write(b'*** EOOH ***' + linesep + linesep)
                self._file.write(message.replace(b'\n', linesep))
        albo_inaczej hasattr(message, 'readline'):
            jeżeli hasattr(message, 'buffer'):
                warnings.warn("Use of text mode files jest deprecated, "
                    "use a binary mode file instead", DeprecationWarning, 3)
                message = message.buffer
            original_pos = message.tell()
            first_pass = Prawda
            dopóki Prawda:
                line = message.readline()
                # Universal newline support.
                jeżeli line.endswith(b'\r\n'):
                    line = line[:-2] + b'\n'
                albo_inaczej line.endswith(b'\r'):
                    line = line[:-1] + b'\n'
                self._file.write(line.replace(b'\n', linesep))
                jeżeli line == b'\n' albo nie line:
                    jeżeli first_pass:
                        first_pass = Nieprawda
                        self._file.write(b'*** EOOH ***' + linesep)
                        message.seek(original_pos)
                    inaczej:
                        przerwij
            dopóki Prawda:
                line = message.readline()
                jeżeli nie line:
                    przerwij
                # Universal newline support.
                jeżeli line.endswith(b'\r\n'):
                    line = line[:-2] + linesep
                albo_inaczej line.endswith(b'\r'):
                    line = line[:-1] + linesep
                albo_inaczej line.endswith(b'\n'):
                    line = line[:-1] + linesep
                self._file.write(line)
        inaczej:
            podnieś TypeError('Invalid message type: %s' % type(message))
        stop = self._file.tell()
        zwróć (start, stop)


klasa Message(email.message.Message):
    """Message przy mailbox-format-specific properties."""

    def __init__(self, message=Nic):
        """Initialize a Message instance."""
        jeżeli isinstance(message, email.message.Message):
            self._become_message(copy.deepcopy(message))
            jeżeli isinstance(message, Message):
                message._explain_to(self)
        albo_inaczej isinstance(message, bytes):
            self._become_message(email.message_from_bytes(message))
        albo_inaczej isinstance(message, str):
            self._become_message(email.message_from_string(message))
        albo_inaczej isinstance(message, io.TextIOWrapper):
            self._become_message(email.message_from_file(message))
        albo_inaczej hasattr(message, "read"):
            self._become_message(email.message_from_binary_file(message))
        albo_inaczej message jest Nic:
            email.message.Message.__init__(self)
        inaczej:
            podnieś TypeError('Invalid message type: %s' % type(message))

    def _become_message(self, message):
        """Assume the non-format-specific state of message."""
        type_specific = getattr(message, '_type_specific_attributes', [])
        dla name w message.__dict__:
            jeżeli name nie w type_specific:
                self.__dict__[name] = message.__dict__[name]

    def _explain_to(self, message):
        """Copy format-specific state to message insofar jako possible."""
        jeżeli isinstance(message, Message):
            zwróć  # There's nothing format-specific to explain.
        inaczej:
            podnieś TypeError('Cannot convert to specified type')


klasa MaildirMessage(Message):
    """Message przy Maildir-specific properties."""

    _type_specific_attributes = ['_subdir', '_info', '_date']

    def __init__(self, message=Nic):
        """Initialize a MaildirMessage instance."""
        self._subdir = 'new'
        self._info = ''
        self._date = time.time()
        Message.__init__(self, message)

    def get_subdir(self):
        """Return 'new' albo 'cur'."""
        zwróć self._subdir

    def set_subdir(self, subdir):
        """Set subdir to 'new' albo 'cur'."""
        jeżeli subdir == 'new' albo subdir == 'cur':
            self._subdir = subdir
        inaczej:
            podnieś ValueError("subdir must be 'new' albo 'cur': %s" % subdir)

    def get_flags(self):
        """Return jako a string the flags that are set."""
        jeżeli self._info.startswith('2,'):
            zwróć self._info[2:]
        inaczej:
            zwróć ''

    def set_flags(self, flags):
        """Set the given flags oraz unset all others."""
        self._info = '2,' + ''.join(sorted(flags))

    def add_flag(self, flag):
        """Set the given flag(s) without changing others."""
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    def remove_flag(self, flag):
        """Unset the given string flag(s) without changing others."""
        jeżeli self.get_flags():
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    def get_date(self):
        """Return delivery date of message, w seconds since the epoch."""
        zwróć self._date

    def set_date(self, date):
        """Set delivery date of message, w seconds since the epoch."""
        spróbuj:
            self._date = float(date)
        wyjąwszy ValueError:
            podnieś TypeError("can't convert to float: %s" % date)

    def get_info(self):
        """Get the message's "info" jako a string."""
        zwróć self._info

    def set_info(self, info):
        """Set the message's "info" string."""
        jeżeli isinstance(info, str):
            self._info = info
        inaczej:
            podnieś TypeError('info must be a string: %s' % type(info))

    def _explain_to(self, message):
        """Copy Maildir-specific state to message insofar jako possible."""
        jeżeli isinstance(message, MaildirMessage):
            message.set_flags(self.get_flags())
            message.set_subdir(self.get_subdir())
            message.set_date(self.get_date())
        albo_inaczej isinstance(message, _mboxMMDFMessage):
            flags = set(self.get_flags())
            jeżeli 'S' w flags:
                message.add_flag('R')
            jeżeli self.get_subdir() == 'cur':
                message.add_flag('O')
            jeżeli 'T' w flags:
                message.add_flag('D')
            jeżeli 'F' w flags:
                message.add_flag('F')
            jeżeli 'R' w flags:
                message.add_flag('A')
            message.set_from('MAILER-DAEMON', time.gmtime(self.get_date()))
        albo_inaczej isinstance(message, MHMessage):
            flags = set(self.get_flags())
            jeżeli 'S' nie w flags:
                message.add_sequence('unseen')
            jeżeli 'R' w flags:
                message.add_sequence('replied')
            jeżeli 'F' w flags:
                message.add_sequence('flagged')
        albo_inaczej isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            jeżeli 'S' nie w flags:
                message.add_label('unseen')
            jeżeli 'T' w flags:
                message.add_label('deleted')
            jeżeli 'R' w flags:
                message.add_label('answered')
            jeżeli 'P' w flags:
                message.add_label('forwarded')
        albo_inaczej isinstance(message, Message):
            dalej
        inaczej:
            podnieś TypeError('Cannot convert to specified type: %s' %
                            type(message))


klasa _mboxMMDFMessage(Message):
    """Message przy mbox- albo MMDF-specific properties."""

    _type_specific_attributes = ['_from']

    def __init__(self, message=Nic):
        """Initialize an mboxMMDFMessage instance."""
        self.set_from('MAILER-DAEMON', Prawda)
        jeżeli isinstance(message, email.message.Message):
            unixz = message.get_unixfrom()
            jeżeli unixz jest nie Nic oraz unixfrom.startswith('From '):
                self.set_from(unixfrom[5:])
        Message.__init__(self, message)

    def get_from(self):
        """Return contents of "From " line."""
        zwróć self._from

    def set_from(self, from_, time_=Nic):
        """Set "From " line, formatting oraz appending time_ jeżeli specified."""
        jeżeli time_ jest nie Nic:
            jeżeli time_ jest Prawda:
                time_ = time.gmtime()
            from_ += ' ' + time.asctime(time_)
        self._z = from_

    def get_flags(self):
        """Return jako a string the flags that are set."""
        zwróć self.get('Status', '') + self.get('X-Status', '')

    def set_flags(self, flags):
        """Set the given flags oraz unset all others."""
        flags = set(flags)
        status_flags, xstatus_flags = '', ''
        dla flag w ('R', 'O'):
            jeżeli flag w flags:
                status_flags += flag
                flags.remove(flag)
        dla flag w ('D', 'F', 'A'):
            jeżeli flag w flags:
                xstatus_flags += flag
                flags.remove(flag)
        xstatus_flags += ''.join(sorted(flags))
        spróbuj:
            self.replace_header('Status', status_flags)
        wyjąwszy KeyError:
            self.add_header('Status', status_flags)
        spróbuj:
            self.replace_header('X-Status', xstatus_flags)
        wyjąwszy KeyError:
            self.add_header('X-Status', xstatus_flags)

    def add_flag(self, flag):
        """Set the given flag(s) without changing others."""
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    def remove_flag(self, flag):
        """Unset the given string flag(s) without changing others."""
        jeżeli 'Status' w self albo 'X-Status' w self:
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    def _explain_to(self, message):
        """Copy mbox- albo MMDF-specific state to message insofar jako possible."""
        jeżeli isinstance(message, MaildirMessage):
            flags = set(self.get_flags())
            jeżeli 'O' w flags:
                message.set_subdir('cur')
            jeżeli 'F' w flags:
                message.add_flag('F')
            jeżeli 'A' w flags:
                message.add_flag('R')
            jeżeli 'R' w flags:
                message.add_flag('S')
            jeżeli 'D' w flags:
                message.add_flag('T')
            usuń message['status']
            usuń message['x-status']
            maybe_date = ' '.join(self.get_from().split()[-5:])
            spróbuj:
                message.set_date(calendar.timegm(time.strptime(maybe_date,
                                                      '%a %b %d %H:%M:%S %Y')))
            wyjąwszy (ValueError, OverflowError):
                dalej
        albo_inaczej isinstance(message, _mboxMMDFMessage):
            message.set_flags(self.get_flags())
            message.set_from(self.get_from())
        albo_inaczej isinstance(message, MHMessage):
            flags = set(self.get_flags())
            jeżeli 'R' nie w flags:
                message.add_sequence('unseen')
            jeżeli 'A' w flags:
                message.add_sequence('replied')
            jeżeli 'F' w flags:
                message.add_sequence('flagged')
            usuń message['status']
            usuń message['x-status']
        albo_inaczej isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            jeżeli 'R' nie w flags:
                message.add_label('unseen')
            jeżeli 'D' w flags:
                message.add_label('deleted')
            jeżeli 'A' w flags:
                message.add_label('answered')
            usuń message['status']
            usuń message['x-status']
        albo_inaczej isinstance(message, Message):
            dalej
        inaczej:
            podnieś TypeError('Cannot convert to specified type: %s' %
                            type(message))


klasa mboxMessage(_mboxMMDFMessage):
    """Message przy mbox-specific properties."""


klasa MHMessage(Message):
    """Message przy MH-specific properties."""

    _type_specific_attributes = ['_sequences']

    def __init__(self, message=Nic):
        """Initialize an MHMessage instance."""
        self._sequences = []
        Message.__init__(self, message)

    def get_sequences(self):
        """Return a list of sequences that include the message."""
        zwróć self._sequences[:]

    def set_sequences(self, sequences):
        """Set the list of sequences that include the message."""
        self._sequences = list(sequences)

    def add_sequence(self, sequence):
        """Add sequence to list of sequences including the message."""
        jeżeli isinstance(sequence, str):
            jeżeli nie sequence w self._sequences:
                self._sequences.append(sequence)
        inaczej:
            podnieś TypeError('sequence type must be str: %s' % type(sequence))

    def remove_sequence(self, sequence):
        """Remove sequence z the list of sequences including the message."""
        spróbuj:
            self._sequences.remove(sequence)
        wyjąwszy ValueError:
            dalej

    def _explain_to(self, message):
        """Copy MH-specific state to message insofar jako possible."""
        jeżeli isinstance(message, MaildirMessage):
            sequences = set(self.get_sequences())
            jeżeli 'unseen' w sequences:
                message.set_subdir('cur')
            inaczej:
                message.set_subdir('cur')
                message.add_flag('S')
            jeżeli 'flagged' w sequences:
                message.add_flag('F')
            jeżeli 'replied' w sequences:
                message.add_flag('R')
        albo_inaczej isinstance(message, _mboxMMDFMessage):
            sequences = set(self.get_sequences())
            jeżeli 'unseen' nie w sequences:
                message.add_flag('RO')
            inaczej:
                message.add_flag('O')
            jeżeli 'flagged' w sequences:
                message.add_flag('F')
            jeżeli 'replied' w sequences:
                message.add_flag('A')
        albo_inaczej isinstance(message, MHMessage):
            dla sequence w self.get_sequences():
                message.add_sequence(sequence)
        albo_inaczej isinstance(message, BabylMessage):
            sequences = set(self.get_sequences())
            jeżeli 'unseen' w sequences:
                message.add_label('unseen')
            jeżeli 'replied' w sequences:
                message.add_label('answered')
        albo_inaczej isinstance(message, Message):
            dalej
        inaczej:
            podnieś TypeError('Cannot convert to specified type: %s' %
                            type(message))


klasa BabylMessage(Message):
    """Message przy Babyl-specific properties."""

    _type_specific_attributes = ['_labels', '_visible']

    def __init__(self, message=Nic):
        """Initialize an BabylMessage instance."""
        self._labels = []
        self._visible = Message()
        Message.__init__(self, message)

    def get_labels(self):
        """Return a list of labels on the message."""
        zwróć self._labels[:]

    def set_labels(self, labels):
        """Set the list of labels on the message."""
        self._labels = list(labels)

    def add_label(self, label):
        """Add label to list of labels on the message."""
        jeżeli isinstance(label, str):
            jeżeli label nie w self._labels:
                self._labels.append(label)
        inaczej:
            podnieś TypeError('label must be a string: %s' % type(label))

    def remove_label(self, label):
        """Remove label z the list of labels on the message."""
        spróbuj:
            self._labels.remove(label)
        wyjąwszy ValueError:
            dalej

    def get_visible(self):
        """Return a Message representation of visible headers."""
        zwróć Message(self._visible)

    def set_visible(self, visible):
        """Set the Message representation of visible headers."""
        self._visible = Message(visible)

    def update_visible(self):
        """Update and/or sensibly generate a set of visible headers."""
        dla header w self._visible.keys():
            jeżeli header w self:
                self._visible.replace_header(header, self[header])
            inaczej:
                usuń self._visible[header]
        dla header w ('Date', 'From', 'Reply-To', 'To', 'CC', 'Subject'):
            jeżeli header w self oraz header nie w self._visible:
                self._visible[header] = self[header]

    def _explain_to(self, message):
        """Copy Babyl-specific state to message insofar jako possible."""
        jeżeli isinstance(message, MaildirMessage):
            labels = set(self.get_labels())
            jeżeli 'unseen' w labels:
                message.set_subdir('cur')
            inaczej:
                message.set_subdir('cur')
                message.add_flag('S')
            jeżeli 'forwarded' w labels albo 'resent' w labels:
                message.add_flag('P')
            jeżeli 'answered' w labels:
                message.add_flag('R')
            jeżeli 'deleted' w labels:
                message.add_flag('T')
        albo_inaczej isinstance(message, _mboxMMDFMessage):
            labels = set(self.get_labels())
            jeżeli 'unseen' nie w labels:
                message.add_flag('RO')
            inaczej:
                message.add_flag('O')
            jeżeli 'deleted' w labels:
                message.add_flag('D')
            jeżeli 'answered' w labels:
                message.add_flag('A')
        albo_inaczej isinstance(message, MHMessage):
            labels = set(self.get_labels())
            jeżeli 'unseen' w labels:
                message.add_sequence('unseen')
            jeżeli 'answered' w labels:
                message.add_sequence('replied')
        albo_inaczej isinstance(message, BabylMessage):
            message.set_visible(self.get_visible())
            dla label w self.get_labels():
                message.add_label(label)
        albo_inaczej isinstance(message, Message):
            dalej
        inaczej:
            podnieś TypeError('Cannot convert to specified type: %s' %
                            type(message))


klasa MMDFMessage(_mboxMMDFMessage):
    """Message przy MMDF-specific properties."""


klasa _ProxyFile:
    """A read-only wrapper of a file."""

    def __init__(self, f, pos=Nic):
        """Initialize a _ProxyFile."""
        self._file = f
        jeżeli pos jest Nic:
            self._pos = f.tell()
        inaczej:
            self._pos = pos

    def read(self, size=Nic):
        """Read bytes."""
        zwróć self._read(size, self._file.read)

    def read1(self, size=Nic):
        """Read bytes."""
        zwróć self._read(size, self._file.read1)

    def readline(self, size=Nic):
        """Read a line."""
        zwróć self._read(size, self._file.readline)

    def readlines(self, sizehint=Nic):
        """Read multiple lines."""
        result = []
        dla line w self:
            result.append(line)
            jeżeli sizehint jest nie Nic:
                sizehint -= len(line)
                jeżeli sizehint <= 0:
                    przerwij
        zwróć result

    def __iter__(self):
        """Iterate over lines."""
        dopóki Prawda:
            line = self.readline()
            jeżeli nie line:
                zwróć
            uzyskaj line

    def tell(self):
        """Return the position."""
        zwróć self._pos

    def seek(self, offset, whence=0):
        """Change position."""
        jeżeli whence == 1:
            self._file.seek(self._pos)
        self._file.seek(offset, whence)
        self._pos = self._file.tell()

    def close(self):
        """Close the file."""
        jeżeli hasattr(self, '_file'):
            spróbuj:
                jeżeli hasattr(self._file, 'close'):
                    self._file.close()
            w_końcu:
                usuń self._file

    def _read(self, size, read_method):
        """Read size bytes using read_method."""
        jeżeli size jest Nic:
            size = -1
        self._file.seek(self._pos)
        result = read_method(size)
        self._pos = self._file.tell()
        zwróć result

    def __enter__(self):
        """Context management protocol support."""
        zwróć self

    def __exit__(self, *exc):
        self.close()

    def readable(self):
        zwróć self._file.readable()

    def writable(self):
        zwróć self._file.writable()

    def seekable(self):
        zwróć self._file.seekable()

    def flush(self):
        zwróć self._file.flush()

    @property
    def closed(self):
        jeżeli nie hasattr(self, '_file'):
            zwróć Prawda
        jeżeli nie hasattr(self._file, 'closed'):
            zwróć Nieprawda
        zwróć self._file.closed


klasa _PartialFile(_ProxyFile):
    """A read-only wrapper of part of a file."""

    def __init__(self, f, start=Nic, stop=Nic):
        """Initialize a _PartialFile."""
        _ProxyFile.__init__(self, f, start)
        self._start = start
        self._stop = stop

    def tell(self):
        """Return the position przy respect to start."""
        zwróć _ProxyFile.tell(self) - self._start

    def seek(self, offset, whence=0):
        """Change position, possibly przy respect to start albo stop."""
        jeżeli whence == 0:
            self._pos = self._start
            whence = 1
        albo_inaczej whence == 2:
            self._pos = self._stop
            whence = 1
        _ProxyFile.seek(self, offset, whence)

    def _read(self, size, read_method):
        """Read size bytes using read_method, honoring start oraz stop."""
        remaining = self._stop - self._pos
        jeżeli remaining <= 0:
            zwróć b''
        jeżeli size jest Nic albo size < 0 albo size > remaining:
            size = remaining
        zwróć _ProxyFile._read(self, size, read_method)

    def close(self):
        # do *not* close the underlying file object dla partial files,
        # since it's global to the mailbox object
        jeżeli hasattr(self, '_file'):
            usuń self._file


def _lock_file(f, dotlock=Prawda):
    """Lock file f using lockf oraz dot locking."""
    dotlock_done = Nieprawda
    spróbuj:
        jeżeli fcntl:
            spróbuj:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            wyjąwszy OSError jako e:
                jeżeli e.errno w (errno.EAGAIN, errno.EACCES, errno.EROFS):
                    podnieś ExternalClashError('lockf: lock unavailable: %s' %
                                             f.name)
                inaczej:
                    podnieś
        jeżeli dotlock:
            spróbuj:
                pre_lock = _create_temporary(f.name + '.lock')
                pre_lock.close()
            wyjąwszy OSError jako e:
                jeżeli e.errno w (errno.EACCES, errno.EROFS):
                    zwróć  # Without write access, just skip dotlocking.
                inaczej:
                    podnieś
            spróbuj:
                jeżeli hasattr(os, 'link'):
                    os.link(pre_lock.name, f.name + '.lock')
                    dotlock_done = Prawda
                    os.unlink(pre_lock.name)
                inaczej:
                    os.rename(pre_lock.name, f.name + '.lock')
                    dotlock_done = Prawda
            wyjąwszy FileExistsError:
                os.remove(pre_lock.name)
                podnieś ExternalClashError('dot lock unavailable: %s' %
                                         f.name)
    wyjąwszy:
        jeżeli fcntl:
            fcntl.lockf(f, fcntl.LOCK_UN)
        jeżeli dotlock_done:
            os.remove(f.name + '.lock')
        podnieś

def _unlock_file(f):
    """Unlock file f using lockf oraz dot locking."""
    jeżeli fcntl:
        fcntl.lockf(f, fcntl.LOCK_UN)
    jeżeli os.path.exists(f.name + '.lock'):
        os.remove(f.name + '.lock')

def _create_carefully(path):
    """Create a file jeżeli it doesn't exist oraz open dla reading oraz writing."""
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o666)
    spróbuj:
        zwróć open(path, 'rb+')
    w_końcu:
        os.close(fd)

def _create_temporary(path):
    """Create a temp file based on path oraz open dla reading oraz writing."""
    zwróć _create_carefully('%s.%s.%s.%s' % (path, int(time.time()),
                                              socket.gethostname(),
                                              os.getpid()))

def _sync_flush(f):
    """Ensure changes to file f are physically on disk."""
    f.flush()
    jeżeli hasattr(os, 'fsync'):
        os.fsync(f.fileno())

def _sync_close(f):
    """Close file f, ensuring all changes are physically on disk."""
    _sync_flush(f)
    f.close()


klasa Error(Exception):
    """Raised dla module-specific errors."""

klasa NoSuchMailboxError(Error):
    """The specified mailbox does nie exist oraz won't be created."""

klasa NotEmptyError(Error):
    """The specified mailbox jest nie empty oraz deletion was requested."""

klasa ExternalClashError(Error):
    """Another process caused an action to fail."""

klasa FormatError(Error):
    """A file appears to have an invalid format."""
