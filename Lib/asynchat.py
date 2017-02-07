# -*- Mode: Python; tab-width: 4 -*-
#       Id: asynchat.py,v 2.26 2000/09/07 22:29:26 rushing Exp
#       Author: Sam Rushing <rushing@nightmare.com>

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

r"""A klasa supporting chat-style (command/response) protocols.

This klasa adds support dla 'chat' style protocols - where one side
sends a 'command', oraz the other sends a response (examples would be
the common internet protocols - smtp, nntp, ftp, etc..).

The handle_read() method looks at the input stream dla the current
'terminator' (usually '\r\n' dla single-line responses, '\r\n.\r\n'
dla multi-line output), calling self.found_terminator() on its
receipt.

dla example:
Say you build an async nntp client using this class.  At the start
of the connection, you'll have self.terminator set to '\r\n', w
order to process the single-line greeting.  Just before issuing a
'LIST' command you'll set it to '\r\n.\r\n'.  The output of the LIST
command will be accumulated (using your own 'collect_incoming_data'
method) up to the terminator, oraz then control will be returned to
you - by calling your self.found_terminator() method.
"""
zaimportuj asyncore
z collections zaimportuj deque


klasa async_chat(asyncore.dispatcher):
    """This jest an abstract class.  You must derive z this class, oraz add
    the two methods collect_incoming_data() oraz found_terminator()"""

    # these are overridable defaults

    ac_in_buffer_size = 65536
    ac_out_buffer_size = 65536

    # we don't want to enable the use of encoding by default, because that jest a
    # sign of an application bug that we don't want to dalej silently

    use_encoding = 0
    encoding = 'latin-1'

    def __init__(self, sock=Nic, map=Nic):
        # dla string terminator matching
        self.ac_in_buffer = b''

        # we use a list here rather than io.BytesIO dla a few reasons...
        # usuń lst[:] jest faster than bio.truncate(0)
        # lst = [] jest faster than bio.truncate(0)
        self.incoming = []

        # we toss the use of the "simple producer" oraz replace it with
        # a pure deque, which the original fifo was a wrapping of
        self.producer_fifo = deque()
        asyncore.dispatcher.__init__(self, sock, map)

    def collect_incoming_data(self, data):
        podnieś NotImplementedError("must be implemented w subclass")

    def _collect_incoming_data(self, data):
        self.incoming.append(data)

    def _get_data(self):
        d = b''.join(self.incoming)
        usuń self.incoming[:]
        zwróć d

    def found_terminator(self):
        podnieś NotImplementedError("must be implemented w subclass")

    def set_terminator(self, term):
        """Set the input delimiter.

        Can be a fixed string of any length, an integer, albo Nic.
        """
        jeżeli isinstance(term, str) oraz self.use_encoding:
            term = bytes(term, self.encoding)
        albo_inaczej isinstance(term, int) oraz term < 0:
            podnieś ValueError('the number of received bytes must be positive')
        self.terminator = term

    def get_terminator(self):
        zwróć self.terminator

    # grab some more data z the socket,
    # throw it to the collector method,
    # check dla the terminator,
    # jeżeli found, transition to the next state.

    def handle_read(self):

        spróbuj:
            data = self.recv(self.ac_in_buffer_size)
        wyjąwszy BlockingIOError:
            zwróć
        wyjąwszy OSError jako why:
            self.handle_error()
            zwróć

        jeżeli isinstance(data, str) oraz self.use_encoding:
            data = bytes(str, self.encoding)
        self.ac_in_buffer = self.ac_in_buffer + data

        # Continue to search dla self.terminator w self.ac_in_buffer,
        # dopóki calling self.collect_incoming_data.  The dopóki loop
        # jest necessary because we might read several data+terminator
        # combos przy a single recv(4096).

        dopóki self.ac_in_buffer:
            lb = len(self.ac_in_buffer)
            terminator = self.get_terminator()
            jeżeli nie terminator:
                # no terminator, collect it all
                self.collect_incoming_data(self.ac_in_buffer)
                self.ac_in_buffer = b''
            albo_inaczej isinstance(terminator, int):
                # numeric terminator
                n = terminator
                jeżeli lb < n:
                    self.collect_incoming_data(self.ac_in_buffer)
                    self.ac_in_buffer = b''
                    self.terminator = self.terminator - lb
                inaczej:
                    self.collect_incoming_data(self.ac_in_buffer[:n])
                    self.ac_in_buffer = self.ac_in_buffer[n:]
                    self.terminator = 0
                    self.found_terminator()
            inaczej:
                # 3 cases:
                # 1) end of buffer matches terminator exactly:
                #    collect data, transition
                # 2) end of buffer matches some prefix:
                #    collect data to the prefix
                # 3) end of buffer does nie match any prefix:
                #    collect data
                terminator_len = len(terminator)
                index = self.ac_in_buffer.find(terminator)
                jeżeli index != -1:
                    # we found the terminator
                    jeżeli index > 0:
                        # don't bother reporting the empty string
                        # (source of subtle bugs)
                        self.collect_incoming_data(self.ac_in_buffer[:index])
                    self.ac_in_buffer = self.ac_in_buffer[index+terminator_len:]
                    # This does the Right Thing jeżeli the terminator
                    # jest changed here.
                    self.found_terminator()
                inaczej:
                    # check dla a prefix of the terminator
                    index = find_prefix_at_end(self.ac_in_buffer, terminator)
                    jeżeli index:
                        jeżeli index != lb:
                            # we found a prefix, collect up to the prefix
                            self.collect_incoming_data(self.ac_in_buffer[:-index])
                            self.ac_in_buffer = self.ac_in_buffer[-index:]
                        przerwij
                    inaczej:
                        # no prefix, collect it all
                        self.collect_incoming_data(self.ac_in_buffer)
                        self.ac_in_buffer = b''

    def handle_write(self):
        self.initiate_send()

    def handle_close(self):
        self.close()

    def push(self, data):
        jeżeli nie isinstance(data, (bytes, bytearray, memoryview)):
            podnieś TypeError('data argument must be byte-ish (%r)',
                            type(data))
        sabs = self.ac_out_buffer_size
        jeżeli len(data) > sabs:
            dla i w range(0, len(data), sabs):
                self.producer_fifo.append(data[i:i+sabs])
        inaczej:
            self.producer_fifo.append(data)
        self.initiate_send()

    def push_with_producer(self, producer):
        self.producer_fifo.append(producer)
        self.initiate_send()

    def readable(self):
        "predicate dla inclusion w the readable dla select()"
        # cannot use the old predicate, it violates the claim of the
        # set_terminator method.

        # zwróć (len(self.ac_in_buffer) <= self.ac_in_buffer_size)
        zwróć 1

    def writable(self):
        "predicate dla inclusion w the writable dla select()"
        zwróć self.producer_fifo albo (nie self.connected)

    def close_when_done(self):
        "automatically close this channel once the outgoing queue jest empty"
        self.producer_fifo.append(Nic)

    def initiate_send(self):
        dopóki self.producer_fifo oraz self.connected:
            first = self.producer_fifo[0]
            # handle empty string/buffer albo Nic entry
            jeżeli nie first:
                usuń self.producer_fifo[0]
                jeżeli first jest Nic:
                    self.handle_close()
                    zwróć

            # handle classic producer behavior
            obs = self.ac_out_buffer_size
            spróbuj:
                data = first[:obs]
            wyjąwszy TypeError:
                data = first.more()
                jeżeli data:
                    self.producer_fifo.appendleft(data)
                inaczej:
                    usuń self.producer_fifo[0]
                kontynuuj

            jeżeli isinstance(data, str) oraz self.use_encoding:
                data = bytes(data, self.encoding)

            # send the data
            spróbuj:
                num_sent = self.send(data)
            wyjąwszy OSError:
                self.handle_error()
                zwróć

            jeżeli num_sent:
                jeżeli num_sent < len(data) albo obs < len(first):
                    self.producer_fifo[0] = first[num_sent:]
                inaczej:
                    usuń self.producer_fifo[0]
            # we tried to send some actual data
            zwróć

    def discard_buffers(self):
        # Emergencies only!
        self.ac_in_buffer = b''
        usuń self.incoming[:]
        self.producer_fifo.clear()


klasa simple_producer:

    def __init__(self, data, buffer_size=512):
        self.data = data
        self.buffer_size = buffer_size

    def more(self):
        jeżeli len(self.data) > self.buffer_size:
            result = self.data[:self.buffer_size]
            self.data = self.data[self.buffer_size:]
            zwróć result
        inaczej:
            result = self.data
            self.data = b''
            zwróć result


klasa fifo:
    def __init__(self, list=Nic):
        zaimportuj warnings
        warnings.warn('fifo klasa will be removed w Python 3.6',
                      DeprecationWarning, stacklevel=2)
        jeżeli nie list:
            self.list = deque()
        inaczej:
            self.list = deque(list)

    def __len__(self):
        zwróć len(self.list)

    def is_empty(self):
        zwróć nie self.list

    def first(self):
        zwróć self.list[0]

    def push(self, data):
        self.list.append(data)

    def pop(self):
        jeżeli self.list:
            zwróć (1, self.list.popleft())
        inaczej:
            zwróć (0, Nic)


# Given 'haystack', see jeżeli any prefix of 'needle' jest at its end.  This
# assumes an exact match has already been checked.  Return the number of
# characters matched.
# dla example:
# f_p_a_e("qwerty\r", "\r\n") => 1
# f_p_a_e("qwertydkjf", "\r\n") => 0
# f_p_a_e("qwerty\r\n", "\r\n") => <undefined>

# this could maybe be made faster przy a computed regex?
# [answer: no; circa Python-2.0, Jan 2001]
# new python:   28961/s
# old python:   18307/s
# re:        12820/s
# regex:     14035/s

def find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    dopóki l oraz nie haystack.endswith(needle[:l]):
        l -= 1
    zwróć l
