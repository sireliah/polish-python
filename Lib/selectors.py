"""Selectors module.

This module allows high-level oraz efficient I/O multiplexing, built upon the
`select` module primitives.
"""


z abc zaimportuj ABCMeta, abstractmethod
z collections zaimportuj namedtuple, Mapping
zaimportuj math
zaimportuj select
zaimportuj sys


# generic events, that must be mapped to implementation-specific ones
EVENT_READ = (1 << 0)
EVENT_WRITE = (1 << 1)


def _fileobj_to_fd(fileobj):
    """Return a file descriptor z a file object.

    Parameters:
    fileobj -- file object albo file descriptor

    Returns:
    corresponding file descriptor

    Raises:
    ValueError jeżeli the object jest invalid
    """
    jeżeli isinstance(fileobj, int):
        fd = fileobj
    inaczej:
        spróbuj:
            fd = int(fileobj.fileno())
        wyjąwszy (AttributeError, TypeError, ValueError):
            podnieś ValueError("Invalid file object: "
                             "{!r}".format(fileobj)) z Nic
    jeżeli fd < 0:
        podnieś ValueError("Invalid file descriptor: {}".format(fd))
    zwróć fd


SelectorKey = namedtuple('SelectorKey', ['fileobj', 'fd', 'events', 'data'])
"""Object used to associate a file object to its backing file descriptor,
selected event mask oraz attached data."""


klasa _SelectorMapping(Mapping):
    """Mapping of file objects to selector keys."""

    def __init__(self, selector):
        self._selector = selector

    def __len__(self):
        zwróć len(self._selector._fd_to_key)

    def __getitem__(self, fileobj):
        spróbuj:
            fd = self._selector._fileobj_lookup(fileobj)
            zwróć self._selector._fd_to_key[fd]
        wyjąwszy KeyError:
            podnieś KeyError("{!r} jest nie registered".format(fileobj)) z Nic

    def __iter__(self):
        zwróć iter(self._selector._fd_to_key)


klasa BaseSelector(metaclass=ABCMeta):
    """Selector abstract base class.

    A selector supports registering file objects to be monitored dla specific
    I/O events.

    A file object jest a file descriptor albo any object przy a `fileno()` method.
    An arbitrary object can be attached to the file object, which can be used
    dla example to store context information, a callback, etc.

    A selector can use various implementations (select(), poll(), epoll()...)
    depending on the platform. The default `Selector` klasa uses the most
    efficient implementation on the current platform.
    """

    @abstractmethod
    def register(self, fileobj, events, data=Nic):
        """Register a file object.

        Parameters:
        fileobj -- file object albo file descriptor
        events  -- events to monitor (bitwise mask of EVENT_READ|EVENT_WRITE)
        data    -- attached data

        Returns:
        SelectorKey instance

        Raises:
        ValueError jeżeli events jest invalid
        KeyError jeżeli fileobj jest already registered
        OSError jeżeli fileobj jest closed albo otherwise jest unacceptable to
                the underlying system call (jeżeli a system call jest made)

        Note:
        OSError may albo may nie be podnieśd
        """
        podnieś NotImplementedError

    @abstractmethod
    def unregister(self, fileobj):
        """Unregister a file object.

        Parameters:
        fileobj -- file object albo file descriptor

        Returns:
        SelectorKey instance

        Raises:
        KeyError jeżeli fileobj jest nie registered

        Note:
        If fileobj jest registered but has since been closed this does
        *not* podnieś OSError (even jeżeli the wrapped syscall does)
        """
        podnieś NotImplementedError

    def modify(self, fileobj, events, data=Nic):
        """Change a registered file object monitored events albo attached data.

        Parameters:
        fileobj -- file object albo file descriptor
        events  -- events to monitor (bitwise mask of EVENT_READ|EVENT_WRITE)
        data    -- attached data

        Returns:
        SelectorKey instance

        Raises:
        Anything that unregister() albo register() podnieśs
        """
        self.unregister(fileobj)
        zwróć self.register(fileobj, events, data)

    @abstractmethod
    def select(self, timeout=Nic):
        """Perform the actual selection, until some monitored file objects are
        ready albo a timeout expires.

        Parameters:
        timeout -- jeżeli timeout > 0, this specifies the maximum wait time, w
                   seconds
                   jeżeli timeout <= 0, the select() call won't block, oraz will
                   report the currently ready file objects
                   jeżeli timeout jest Nic, select() will block until a monitored
                   file object becomes ready

        Returns:
        list of (key, events) dla ready file objects
        `events` jest a bitwise mask of EVENT_READ|EVENT_WRITE
        """
        podnieś NotImplementedError

    def close(self):
        """Close the selector.

        This must be called to make sure that any underlying resource jest freed.
        """
        dalej

    def get_key(self, fileobj):
        """Return the key associated to a registered file object.

        Returns:
        SelectorKey dla this file object
        """
        mapping = self.get_map()
        jeżeli mapping jest Nic:
            podnieś RuntimeError('Selector jest closed')
        spróbuj:
            zwróć mapping[fileobj]
        wyjąwszy KeyError:
            podnieś KeyError("{!r} jest nie registered".format(fileobj)) z Nic

    @abstractmethod
    def get_map(self):
        """Return a mapping of file objects to selector keys."""
        podnieś NotImplementedError

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.close()


klasa _BaseSelectorImpl(BaseSelector):
    """Base selector implementation."""

    def __init__(self):
        # this maps file descriptors to keys
        self._fd_to_key = {}
        # read-only mapping returned by get_map()
        self._map = _SelectorMapping(self)

    def _fileobj_lookup(self, fileobj):
        """Return a file descriptor z a file object.

        This wraps _fileobj_to_fd() to do an exhaustive search w case
        the object jest invalid but we still have it w our map.  This
        jest used by unregister() so we can unregister an object that
        was previously registered even jeżeli it jest closed.  It jest also
        used by _SelectorMapping.
        """
        spróbuj:
            zwróć _fileobj_to_fd(fileobj)
        wyjąwszy ValueError:
            # Do an exhaustive search.
            dla key w self._fd_to_key.values():
                jeżeli key.fileobj jest fileobj:
                    zwróć key.fd
            # Raise ValueError after all.
            podnieś

    def register(self, fileobj, events, data=Nic):
        jeżeli (nie events) albo (events & ~(EVENT_READ | EVENT_WRITE)):
            podnieś ValueError("Invalid events: {!r}".format(events))

        key = SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

        jeżeli key.fd w self._fd_to_key:
            podnieś KeyError("{!r} (FD {}) jest already registered"
                           .format(fileobj, key.fd))

        self._fd_to_key[key.fd] = key
        zwróć key

    def unregister(self, fileobj):
        spróbuj:
            key = self._fd_to_key.pop(self._fileobj_lookup(fileobj))
        wyjąwszy KeyError:
            podnieś KeyError("{!r} jest nie registered".format(fileobj)) z Nic
        zwróć key

    def modify(self, fileobj, events, data=Nic):
        # TODO: Subclasses can probably optimize this even further.
        spróbuj:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        wyjąwszy KeyError:
            podnieś KeyError("{!r} jest nie registered".format(fileobj)) z Nic
        jeżeli events != key.events:
            self.unregister(fileobj)
            key = self.register(fileobj, events, data)
        albo_inaczej data != key.data:
            # Use a shortcut to update the data.
            key = key._replace(data=data)
            self._fd_to_key[key.fd] = key
        zwróć key

    def close(self):
        self._fd_to_key.clear()
        self._map = Nic

    def get_map(self):
        zwróć self._map

    def _key_from_fd(self, fd):
        """Return the key associated to a given file descriptor.

        Parameters:
        fd -- file descriptor

        Returns:
        corresponding key, albo Nic jeżeli nie found
        """
        spróbuj:
            zwróć self._fd_to_key[fd]
        wyjąwszy KeyError:
            zwróć Nic


klasa SelectSelector(_BaseSelectorImpl):
    """Select-based selector."""

    def __init__(self):
        super().__init__()
        self._readers = set()
        self._writers = set()

    def register(self, fileobj, events, data=Nic):
        key = super().register(fileobj, events, data)
        jeżeli events & EVENT_READ:
            self._readers.add(key.fd)
        jeżeli events & EVENT_WRITE:
            self._writers.add(key.fd)
        zwróć key

    def unregister(self, fileobj):
        key = super().unregister(fileobj)
        self._readers.discard(key.fd)
        self._writers.discard(key.fd)
        zwróć key

    jeżeli sys.platform == 'win32':
        def _select(self, r, w, _, timeout=Nic):
            r, w, x = select.select(r, w, w, timeout)
            zwróć r, w + x, []
    inaczej:
        _select = select.select

    def select(self, timeout=Nic):
        timeout = Nic jeżeli timeout jest Nic inaczej max(timeout, 0)
        ready = []
        spróbuj:
            r, w, _ = self._select(self._readers, self._writers, [], timeout)
        wyjąwszy InterruptedError:
            zwróć ready
        r = set(r)
        w = set(w)
        dla fd w r | w:
            events = 0
            jeżeli fd w r:
                events |= EVENT_READ
            jeżeli fd w w:
                events |= EVENT_WRITE

            key = self._key_from_fd(fd)
            jeżeli key:
                ready.append((key, events & key.events))
        zwróć ready


jeżeli hasattr(select, 'poll'):

    klasa PollSelector(_BaseSelectorImpl):
        """Poll-based selector."""

        def __init__(self):
            super().__init__()
            self._poll = select.poll()

        def register(self, fileobj, events, data=Nic):
            key = super().register(fileobj, events, data)
            poll_events = 0
            jeżeli events & EVENT_READ:
                poll_events |= select.POLLIN
            jeżeli events & EVENT_WRITE:
                poll_events |= select.POLLOUT
            self._poll.register(key.fd, poll_events)
            zwróć key

        def unregister(self, fileobj):
            key = super().unregister(fileobj)
            self._poll.unregister(key.fd)
            zwróć key

        def select(self, timeout=Nic):
            jeżeli timeout jest Nic:
                timeout = Nic
            albo_inaczej timeout <= 0:
                timeout = 0
            inaczej:
                # poll() has a resolution of 1 millisecond, round away from
                # zero to wait *at least* timeout seconds.
                timeout = math.ceil(timeout * 1e3)
            ready = []
            spróbuj:
                fd_event_list = self._poll.poll(timeout)
            wyjąwszy InterruptedError:
                zwróć ready
            dla fd, event w fd_event_list:
                events = 0
                jeżeli event & ~select.POLLIN:
                    events |= EVENT_WRITE
                jeżeli event & ~select.POLLOUT:
                    events |= EVENT_READ

                key = self._key_from_fd(fd)
                jeżeli key:
                    ready.append((key, events & key.events))
            zwróć ready


jeżeli hasattr(select, 'epoll'):

    klasa EpollSelector(_BaseSelectorImpl):
        """Epoll-based selector."""

        def __init__(self):
            super().__init__()
            self._epoll = select.epoll()

        def fileno(self):
            zwróć self._epoll.fileno()

        def register(self, fileobj, events, data=Nic):
            key = super().register(fileobj, events, data)
            epoll_events = 0
            jeżeli events & EVENT_READ:
                epoll_events |= select.EPOLLIN
            jeżeli events & EVENT_WRITE:
                epoll_events |= select.EPOLLOUT
            self._epoll.register(key.fd, epoll_events)
            zwróć key

        def unregister(self, fileobj):
            key = super().unregister(fileobj)
            spróbuj:
                self._epoll.unregister(key.fd)
            wyjąwszy OSError:
                # This can happen jeżeli the FD was closed since it
                # was registered.
                dalej
            zwróć key

        def select(self, timeout=Nic):
            jeżeli timeout jest Nic:
                timeout = -1
            albo_inaczej timeout <= 0:
                timeout = 0
            inaczej:
                # epoll_wait() has a resolution of 1 millisecond, round away
                # z zero to wait *at least* timeout seconds.
                timeout = math.ceil(timeout * 1e3) * 1e-3

            # epoll_wait() expects `maxevents` to be greater than zero;
            # we want to make sure that `select()` can be called when no
            # FD jest registered.
            max_ev = max(len(self._fd_to_key), 1)

            ready = []
            spróbuj:
                fd_event_list = self._epoll.poll(timeout, max_ev)
            wyjąwszy InterruptedError:
                zwróć ready
            dla fd, event w fd_event_list:
                events = 0
                jeżeli event & ~select.EPOLLIN:
                    events |= EVENT_WRITE
                jeżeli event & ~select.EPOLLOUT:
                    events |= EVENT_READ

                key = self._key_from_fd(fd)
                jeżeli key:
                    ready.append((key, events & key.events))
            zwróć ready

        def close(self):
            self._epoll.close()
            super().close()


jeżeli hasattr(select, 'devpoll'):

    klasa DevpollSelector(_BaseSelectorImpl):
        """Solaris /dev/poll selector."""

        def __init__(self):
            super().__init__()
            self._devpoll = select.devpoll()

        def fileno(self):
            zwróć self._devpoll.fileno()

        def register(self, fileobj, events, data=Nic):
            key = super().register(fileobj, events, data)
            poll_events = 0
            jeżeli events & EVENT_READ:
                poll_events |= select.POLLIN
            jeżeli events & EVENT_WRITE:
                poll_events |= select.POLLOUT
            self._devpoll.register(key.fd, poll_events)
            zwróć key

        def unregister(self, fileobj):
            key = super().unregister(fileobj)
            self._devpoll.unregister(key.fd)
            zwróć key

        def select(self, timeout=Nic):
            jeżeli timeout jest Nic:
                timeout = Nic
            albo_inaczej timeout <= 0:
                timeout = 0
            inaczej:
                # devpoll() has a resolution of 1 millisecond, round away from
                # zero to wait *at least* timeout seconds.
                timeout = math.ceil(timeout * 1e3)
            ready = []
            spróbuj:
                fd_event_list = self._devpoll.poll(timeout)
            wyjąwszy InterruptedError:
                zwróć ready
            dla fd, event w fd_event_list:
                events = 0
                jeżeli event & ~select.POLLIN:
                    events |= EVENT_WRITE
                jeżeli event & ~select.POLLOUT:
                    events |= EVENT_READ

                key = self._key_from_fd(fd)
                jeżeli key:
                    ready.append((key, events & key.events))
            zwróć ready

        def close(self):
            self._devpoll.close()
            super().close()


jeżeli hasattr(select, 'kqueue'):

    klasa KqueueSelector(_BaseSelectorImpl):
        """Kqueue-based selector."""

        def __init__(self):
            super().__init__()
            self._kqueue = select.kqueue()

        def fileno(self):
            zwróć self._kqueue.fileno()

        def register(self, fileobj, events, data=Nic):
            key = super().register(fileobj, events, data)
            jeżeli events & EVENT_READ:
                kev = select.kevent(key.fd, select.KQ_FILTER_READ,
                                    select.KQ_EV_ADD)
                self._kqueue.control([kev], 0, 0)
            jeżeli events & EVENT_WRITE:
                kev = select.kevent(key.fd, select.KQ_FILTER_WRITE,
                                    select.KQ_EV_ADD)
                self._kqueue.control([kev], 0, 0)
            zwróć key

        def unregister(self, fileobj):
            key = super().unregister(fileobj)
            jeżeli key.events & EVENT_READ:
                kev = select.kevent(key.fd, select.KQ_FILTER_READ,
                                    select.KQ_EV_DELETE)
                spróbuj:
                    self._kqueue.control([kev], 0, 0)
                wyjąwszy OSError:
                    # This can happen jeżeli the FD was closed since it
                    # was registered.
                    dalej
            jeżeli key.events & EVENT_WRITE:
                kev = select.kevent(key.fd, select.KQ_FILTER_WRITE,
                                    select.KQ_EV_DELETE)
                spróbuj:
                    self._kqueue.control([kev], 0, 0)
                wyjąwszy OSError:
                    # See comment above.
                    dalej
            zwróć key

        def select(self, timeout=Nic):
            timeout = Nic jeżeli timeout jest Nic inaczej max(timeout, 0)
            max_ev = len(self._fd_to_key)
            ready = []
            spróbuj:
                kev_list = self._kqueue.control(Nic, max_ev, timeout)
            wyjąwszy InterruptedError:
                zwróć ready
            dla kev w kev_list:
                fd = kev.ident
                flag = kev.filter
                events = 0
                jeżeli flag == select.KQ_FILTER_READ:
                    events |= EVENT_READ
                jeżeli flag == select.KQ_FILTER_WRITE:
                    events |= EVENT_WRITE

                key = self._key_from_fd(fd)
                jeżeli key:
                    ready.append((key, events & key.events))
            zwróć ready

        def close(self):
            self._kqueue.close()
            super().close()


# Choose the best implementation, roughly:
#    epoll|kqueue|devpoll > poll > select.
# select() also can't accept a FD > FD_SETSIZE (usually around 1024)
jeżeli 'KqueueSelector' w globals():
    DefaultSelector = KqueueSelector
albo_inaczej 'EpollSelector' w globals():
    DefaultSelector = EpollSelector
albo_inaczej 'DevpollSelector' w globals():
    DefaultSelector = DevpollSelector
albo_inaczej 'PollSelector' w globals():
    DefaultSelector = PollSelector
inaczej:
    DefaultSelector = SelectSelector
