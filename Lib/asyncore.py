# -*- Mode: Python -*-
#   Id: asyncore.py,v 2.51 2000/09/07 22:29:26 rushing Exp
#   Author: Sam Rushing <rushing@nightmare.com>

# ======================================================================
# Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, oraz distribute this software oraz
# its documentation dla any purpose oraz without fee jest hereby
# granted, provided that the above copyright notice appear w all
# copies oraz that both that copyright notice oraz this permission
# notice appear w supporting documentation, oraz that the name of Sam
# Rushing nie be used w advertising albo publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================

"""Basic infrastructure dla asynchronous socket service clients oraz servers.

There are only two ways to have a program on a single processor do "more
than one thing at a time".  Multi-threaded programming jest the simplest oraz
most popular way to do it, but there jest another very different technique,
that lets you have nearly all the advantages of multi-threading, without
actually using multiple threads. it's really only practical jeżeli your program
is largely I/O bound. If your program jest CPU bound, then pre-emptive
scheduled threads are probably what you really need. Network servers are
rarely CPU-bound, however.

If your operating system supports the select() system call w its I/O
library (and nearly all do), then you can use it to juggle multiple
communication channels at once; doing other work dopóki your I/O jest taking
place w the "background."  Although this strategy can seem strange oraz
complex, especially at first, it jest w many ways easier to understand oraz
control than multi-threaded programming. The module documented here solves
many of the difficult problems dla you, making the task of building
sophisticated high-performance network servers oraz clients a snap.
"""

zaimportuj select
zaimportuj socket
zaimportuj sys
zaimportuj time
zaimportuj warnings

zaimportuj os
z errno zaimportuj EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
     ENOTCONN, ESHUTDOWN, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN, \
     errorcode

_DISCONNECTED = frozenset({ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE,
                           EBADF})

spróbuj:
    socket_map
wyjąwszy NameError:
    socket_map = {}

def _strerror(err):
    spróbuj:
        zwróć os.strerror(err)
    wyjąwszy (ValueError, OverflowError, NameError):
        jeżeli err w errorcode:
            zwróć errorcode[err]
        zwróć "Unknown error %s" %err

klasa ExitNow(Exception):
    dalej

_reraised_exceptions = (ExitNow, KeyboardInterrupt, SystemExit)

def read(obj):
    spróbuj:
        obj.handle_read_event()
    wyjąwszy _reraised_exceptions:
        podnieś
    wyjąwszy:
        obj.handle_error()

def write(obj):
    spróbuj:
        obj.handle_write_event()
    wyjąwszy _reraised_exceptions:
        podnieś
    wyjąwszy:
        obj.handle_error()

def _exception(obj):
    spróbuj:
        obj.handle_expt_event()
    wyjąwszy _reraised_exceptions:
        podnieś
    wyjąwszy:
        obj.handle_error()

def readwrite(obj, flags):
    spróbuj:
        jeżeli flags & select.POLLIN:
            obj.handle_read_event()
        jeżeli flags & select.POLLOUT:
            obj.handle_write_event()
        jeżeli flags & select.POLLPRI:
            obj.handle_expt_event()
        jeżeli flags & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            obj.handle_close()
    wyjąwszy OSError jako e:
        jeżeli e.args[0] nie w _DISCONNECTED:
            obj.handle_error()
        inaczej:
            obj.handle_close()
    wyjąwszy _reraised_exceptions:
        podnieś
    wyjąwszy:
        obj.handle_error()

def poll(timeout=0.0, map=Nic):
    jeżeli map jest Nic:
        map = socket_map
    jeżeli map:
        r = []; w = []; e = []
        dla fd, obj w list(map.items()):
            is_r = obj.readable()
            is_w = obj.writable()
            jeżeli is_r:
                r.append(fd)
            # accepting sockets should nie be writable
            jeżeli is_w oraz nie obj.accepting:
                w.append(fd)
            jeżeli is_r albo is_w:
                e.append(fd)
        jeżeli [] == r == w == e:
            time.sleep(timeout)
            zwróć

        r, w, e = select.select(r, w, e, timeout)

        dla fd w r:
            obj = map.get(fd)
            jeżeli obj jest Nic:
                kontynuuj
            read(obj)

        dla fd w w:
            obj = map.get(fd)
            jeżeli obj jest Nic:
                kontynuuj
            write(obj)

        dla fd w e:
            obj = map.get(fd)
            jeżeli obj jest Nic:
                kontynuuj
            _exception(obj)

def poll2(timeout=0.0, map=Nic):
    # Use the poll() support added to the select module w Python 2.0
    jeżeli map jest Nic:
        map = socket_map
    jeżeli timeout jest nie Nic:
        # timeout jest w milliseconds
        timeout = int(timeout*1000)
    pollster = select.poll()
    jeżeli map:
        dla fd, obj w list(map.items()):
            flags = 0
            jeżeli obj.readable():
                flags |= select.POLLIN | select.POLLPRI
            # accepting sockets should nie be writable
            jeżeli obj.writable() oraz nie obj.accepting:
                flags |= select.POLLOUT
            jeżeli flags:
                pollster.register(fd, flags)

        r = pollster.poll(timeout)
        dla fd, flags w r:
            obj = map.get(fd)
            jeżeli obj jest Nic:
                kontynuuj
            readwrite(obj, flags)

poll3 = poll2                           # Alias dla backward compatibility

def loop(timeout=30.0, use_poll=Nieprawda, map=Nic, count=Nic):
    jeżeli map jest Nic:
        map = socket_map

    jeżeli use_poll oraz hasattr(select, 'poll'):
        poll_fun = poll2
    inaczej:
        poll_fun = poll

    jeżeli count jest Nic:
        dopóki map:
            poll_fun(timeout, map)

    inaczej:
        dopóki map oraz count > 0:
            poll_fun(timeout, map)
            count = count - 1

klasa dispatcher:

    debug = Nieprawda
    connected = Nieprawda
    accepting = Nieprawda
    connecting = Nieprawda
    closing = Nieprawda
    addr = Nic
    ignore_log_types = frozenset({'warning'})

    def __init__(self, sock=Nic, map=Nic):
        jeżeli map jest Nic:
            self._map = socket_map
        inaczej:
            self._map = map

        self._fileno = Nic

        jeżeli sock:
            # Set to nonblocking just to make sure dla cases where we
            # get a socket z a blocking source.
            sock.setblocking(0)
            self.set_socket(sock, map)
            self.connected = Prawda
            # The constructor no longer requires that the socket
            # dalejed be connected.
            spróbuj:
                self.addr = sock.getpeername()
            wyjąwszy OSError jako err:
                jeżeli err.args[0] w (ENOTCONN, EINVAL):
                    # To handle the case where we got an unconnected
                    # socket.
                    self.connected = Nieprawda
                inaczej:
                    # The socket jest broken w some unknown way, alert
                    # the user oraz remove it z the map (to prevent
                    # polling of broken sockets).
                    self.del_channel(map)
                    podnieś
        inaczej:
            self.socket = Nic

    def __repr__(self):
        status = [self.__class__.__module__+"."+self.__class__.__qualname__]
        jeżeli self.accepting oraz self.addr:
            status.append('listening')
        albo_inaczej self.connected:
            status.append('connected')
        jeżeli self.addr jest nie Nic:
            spróbuj:
                status.append('%s:%d' % self.addr)
            wyjąwszy TypeError:
                status.append(repr(self.addr))
        zwróć '<%s at %#x>' % (' '.join(status), id(self))

    __str__ = __repr__

    def add_channel(self, map=Nic):
        #self.log_info('adding channel %s' % self)
        jeżeli map jest Nic:
            map = self._map
        map[self._fileno] = self

    def del_channel(self, map=Nic):
        fd = self._fileno
        jeżeli map jest Nic:
            map = self._map
        jeżeli fd w map:
            #self.log_info('closing channel %d:%s' % (fd, self))
            usuń map[fd]
        self._fileno = Nic

    def create_socket(self, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.family_and_type = family, type
        sock = socket.socket(family, type)
        sock.setblocking(0)
        self.set_socket(sock)

    def set_socket(self, sock, map=Nic):
        self.socket = sock
##        self.__dict__['socket'] = sock
        self._fileno = sock.fileno()
        self.add_channel(map)

    def set_reuse_addr(self):
        # try to re-use a server port jeżeli possible
        spróbuj:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        wyjąwszy OSError:
            dalej

    # ==================================================
    # predicates dla select()
    # these are used jako filters dla the lists of sockets
    # to dalej to select().
    # ==================================================

    def readable(self):
        zwróć Prawda

    def writable(self):
        zwróć Prawda

    # ==================================================
    # socket object methods.
    # ==================================================

    def listen(self, num):
        self.accepting = Prawda
        jeżeli os.name == 'nt' oraz num > 5:
            num = 5
        zwróć self.socket.listen(num)

    def bind(self, addr):
        self.addr = addr
        zwróć self.socket.bind(addr)

    def connect(self, address):
        self.connected = Nieprawda
        self.connecting = Prawda
        err = self.socket.connect_ex(address)
        jeżeli err w (EINPROGRESS, EALREADY, EWOULDBLOCK) \
        albo err == EINVAL oraz os.name w ('nt', 'ce'):
            self.addr = address
            zwróć
        jeżeli err w (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        inaczej:
            podnieś OSError(err, errorcode[err])

    def accept(self):
        # XXX can zwróć either an address pair albo Nic
        spróbuj:
            conn, addr = self.socket.accept()
        wyjąwszy TypeError:
            zwróć Nic
        wyjąwszy OSError jako why:
            jeżeli why.args[0] w (EWOULDBLOCK, ECONNABORTED, EAGAIN):
                zwróć Nic
            inaczej:
                podnieś
        inaczej:
            zwróć conn, addr

    def send(self, data):
        spróbuj:
            result = self.socket.send(data)
            zwróć result
        wyjąwszy OSError jako why:
            jeżeli why.args[0] == EWOULDBLOCK:
                zwróć 0
            albo_inaczej why.args[0] w _DISCONNECTED:
                self.handle_close()
                zwróć 0
            inaczej:
                podnieś

    def recv(self, buffer_size):
        spróbuj:
            data = self.socket.recv(buffer_size)
            jeżeli nie data:
                # a closed connection jest indicated by signaling
                # a read condition, oraz having recv() zwróć 0.
                self.handle_close()
                zwróć b''
            inaczej:
                zwróć data
        wyjąwszy OSError jako why:
            # winsock sometimes podnieśs ENOTCONN
            jeżeli why.args[0] w _DISCONNECTED:
                self.handle_close()
                zwróć b''
            inaczej:
                podnieś

    def close(self):
        self.connected = Nieprawda
        self.accepting = Nieprawda
        self.connecting = Nieprawda
        self.del_channel()
        jeżeli self.socket jest nie Nic:
            spróbuj:
                self.socket.close()
            wyjąwszy OSError jako why:
                jeżeli why.args[0] nie w (ENOTCONN, EBADF):
                    podnieś

    # log oraz log_info may be overridden to provide more sophisticated
    # logging oraz warning methods. In general, log jest dla 'hit' logging
    # oraz 'log_info' jest dla informational, warning oraz error logging.

    def log(self, message):
        sys.stderr.write('log: %s\n' % str(message))

    def log_info(self, message, type='info'):
        jeżeli type nie w self.ignore_log_types:
            print('%s: %s' % (type, message))

    def handle_read_event(self):
        jeżeli self.accepting:
            # accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        albo_inaczej nie self.connected:
            jeżeli self.connecting:
                self.handle_connect_event()
            self.handle_read()
        inaczej:
            self.handle_read()

    def handle_connect_event(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        jeżeli err != 0:
            podnieś OSError(err, _strerror(err))
        self.handle_connect()
        self.connected = Prawda
        self.connecting = Nieprawda

    def handle_write_event(self):
        jeżeli self.accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            zwróć

        jeżeli nie self.connected:
            jeżeli self.connecting:
                self.handle_connect_event()
        self.handle_write()

    def handle_expt_event(self):
        # handle_expt_event() jest called jeżeli there might be an error on the
        # socket, albo jeżeli there jest OOB data
        # check dla the error condition first
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        jeżeli err != 0:
            # we can get here when select.select() says that there jest an
            # exceptional condition on the socket
            # since there jest an error, we'll go ahead oraz close the socket
            # like we would w a subclassed handle_read() that received no
            # data
            self.handle_close()
        inaczej:
            self.handle_expt()

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        spróbuj:
            self_repr = repr(self)
        wyjąwszy:
            self_repr = '<__repr__(self) failed dla object at %0x>' % id(self)

        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                ),
            'error'
            )
        self.handle_close()

    def handle_expt(self):
        self.log_info('unhandled incoming priority event', 'warning')

    def handle_read(self):
        self.log_info('unhandled read event', 'warning')

    def handle_write(self):
        self.log_info('unhandled write event', 'warning')

    def handle_connect(self):
        self.log_info('unhandled connect event', 'warning')

    def handle_accept(self):
        pair = self.accept()
        jeżeli pair jest nie Nic:
            self.handle_accepted(*pair)

    def handle_accepted(self, sock, addr):
        sock.close()
        self.log_info('unhandled accepted event', 'warning')

    def handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()

# ---------------------------------------------------------------------------
# adds simple buffered output capability, useful dla simple clients.
# [dla more sophisticated usage use asynchat.async_chat]
# ---------------------------------------------------------------------------

klasa dispatcher_with_send(dispatcher):

    def __init__(self, sock=Nic, map=Nic):
        dispatcher.__init__(self, sock, map)
        self.out_buffer = b''

    def initiate_send(self):
        num_sent = 0
        num_sent = dispatcher.send(self, self.out_buffer[:65536])
        self.out_buffer = self.out_buffer[num_sent:]

    def handle_write(self):
        self.initiate_send()

    def writable(self):
        zwróć (nie self.connected) albo len(self.out_buffer)

    def send(self, data):
        jeżeli self.debug:
            self.log_info('sending %s' % repr(data))
        self.out_buffer = self.out_buffer + data
        self.initiate_send()

# ---------------------------------------------------------------------------
# used dla debugging.
# ---------------------------------------------------------------------------

def compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    jeżeli nie tb: # Must have a traceback
        podnieś AssertionError("traceback does nie exist")
    dopóki tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
            ))
        tb = tb.tb_next

    # just to be safe
    usuń tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x dla x w tbinfo])
    zwróć (file, function, line), t, v, info

def close_all(map=Nic, ignore_all=Nieprawda):
    jeżeli map jest Nic:
        map = socket_map
    dla x w list(map.values()):
        spróbuj:
            x.close()
        wyjąwszy OSError jako x:
            jeżeli x.args[0] == EBADF:
                dalej
            albo_inaczej nie ignore_all:
                podnieś
        wyjąwszy _reraised_exceptions:
            podnieś
        wyjąwszy:
            jeżeli nie ignore_all:
                podnieś
    map.clear()

# Asynchronous File I/O:
#
# After a little research (reading man pages on various unixen, oraz
# digging through the linux kernel), I've determined that select()
# isn't meant dla doing asynchronous file i/o.
# Heartening, though - reading linux/mm/filemap.c shows that linux
# supports asynchronous read-ahead.  So _MOST_ of the time, the data
# will be sitting w memory dla us already when we go to read it.
#
# What other OS's (besides NT) support async file i/o?  [VMS?]
#
# Regardless, this jest useful dla pipes, oraz stdin/stdout...

jeżeli os.name == 'posix':
    klasa file_wrapper:
        # Here we override just enough to make a file
        # look like a socket dla the purposes of asyncore.
        # The dalejed fd jest automatically os.dup()'d

        def __init__(self, fd):
            self.fd = os.dup(fd)

        def __del__(self):
            jeżeli self.fd >= 0:
                warnings.warn("unclosed file %r" % self, ResourceWarning)
            self.close()

        def recv(self, *args):
            zwróć os.read(self.fd, *args)

        def send(self, *args):
            zwróć os.write(self.fd, *args)

        def getsockopt(self, level, optname, buflen=Nic):
            jeżeli (level == socket.SOL_SOCKET oraz
                optname == socket.SO_ERROR oraz
                nie buflen):
                zwróć 0
            podnieś NotImplementedError("Only asyncore specific behaviour "
                                      "implemented.")

        read = recv
        write = send

        def close(self):
            jeżeli self.fd < 0:
                zwróć
            os.close(self.fd)
            self.fd = -1

        def fileno(self):
            zwróć self.fd

    klasa file_dispatcher(dispatcher):

        def __init__(self, fd, map=Nic):
            dispatcher.__init__(self, Nic, map)
            self.connected = Prawda
            spróbuj:
                fd = fd.fileno()
            wyjąwszy AttributeError:
                dalej
            self.set_file(fd)
            # set it to non-blocking mode
            os.set_blocking(fd, Nieprawda)

        def set_file(self, fd):
            self.socket = file_wrapper(fd)
            self._fileno = self.socket.fileno()
            self.add_channel()
