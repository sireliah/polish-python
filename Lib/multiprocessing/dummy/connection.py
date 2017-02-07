#
# Analogue of `multiprocessing.connection` which uses queues instead of sockets
#
# multiprocessing/dummy/connection.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [ 'Client', 'Listener', 'Pipe' ]

z queue zaimportuj Queue


families = [Nic]


klasa Listener(object):

    def __init__(self, address=Nic, family=Nic, backlog=1):
        self._backlog_queue = Queue(backlog)

    def accept(self):
        zwróć Connection(*self._backlog_queue.get())

    def close(self):
        self._backlog_queue = Nic

    address = property(lambda self: self._backlog_queue)

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


def Client(address):
    _in, _out = Queue(), Queue()
    address.put((_out, _in))
    zwróć Connection(_in, _out)


def Pipe(duplex=Prawda):
    a, b = Queue(), Queue()
    zwróć Connection(a, b), Connection(b, a)


klasa Connection(object):

    def __init__(self, _in, _out):
        self._out = _out
        self._in = _in
        self.send = self.send_bytes = _out.put
        self.recv = self.recv_bytes = _in.get

    def poll(self, timeout=0.0):
        jeżeli self._in.qsize() > 0:
            zwróć Prawda
        jeżeli timeout <= 0.0:
            zwróć Nieprawda
        przy self._in.not_empty:
            self._in.not_empty.wait(timeout)
        zwróć self._in.qsize() > 0

    def close(self):
        dalej

    def __enter__(self):
        zwróć self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
