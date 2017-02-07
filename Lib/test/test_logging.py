# Copyright 2001-2014 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, oraz distribute this software oraz its
# documentation dla any purpose oraz without fee jest hereby granted,
# provided that the above copyright notice appear w all copies oraz that
# both that copyright notice oraz this permission notice appear w
# supporting documentation, oraz that the name of Vinay Sajip
# nie be used w advertising albo publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Test harness dla the logging module. Run all tests.

Copyright (C) 2001-2014 Vinay Sajip. All Rights Reserved.
"""

zaimportuj logging
zaimportuj logging.handlers
zaimportuj logging.config

zaimportuj codecs
zaimportuj configparser
zaimportuj datetime
zaimportuj pickle
zaimportuj io
zaimportuj gc
zaimportuj json
zaimportuj os
zaimportuj queue
zaimportuj random
zaimportuj re
zaimportuj socket
zaimportuj struct
zaimportuj sys
zaimportuj tempfile
z test.support.script_helper zaimportuj assert_python_ok
z test zaimportuj support
zaimportuj textwrap
zaimportuj time
zaimportuj unittest
zaimportuj warnings
zaimportuj weakref
spróbuj:
    zaimportuj threading
    # The following imports are needed only dla tests which
    # require threading
    zaimportuj asyncore
    z http.server zaimportuj HTTPServer, BaseHTTPRequestHandler
    zaimportuj smtpd
    z urllib.parse zaimportuj urlparse, parse_qs
    z socketserver zaimportuj (ThreadingUDPServer, DatagramRequestHandler,
                              ThreadingTCPServer, StreamRequestHandler)
wyjąwszy ImportError:
    threading = Nic
spróbuj:
    zaimportuj win32evtlog
wyjąwszy ImportError:
    win32evtlog = Nic
spróbuj:
    zaimportuj win32evtlogutil
wyjąwszy ImportError:
    win32evtlogutil = Nic
    win32evtlog = Nic
spróbuj:
    zaimportuj zlib
wyjąwszy ImportError:
    dalej

klasa BaseTest(unittest.TestCase):

    """Base klasa dla logging tests."""

    log_format = "%(name)s -> %(levelname)s: %(message)s"
    expected_log_pat = r"^([\w.]+) -> (\w+): (\d+)$"
    message_num = 0

    def setUp(self):
        """Setup the default logging stream to an internal StringIO instance,
        so that we can examine log output jako we want."""
        logger_dict = logging.getLogger().manager.loggerDict
        logging._acquireLock()
        spróbuj:
            self.saved_handlers = logging._handlers.copy()
            self.saved_handler_list = logging._handlerList[:]
            self.saved_loggers = saved_loggers = logger_dict.copy()
            self.saved_name_to_level = logging._nameToLevel.copy()
            self.saved_level_to_name = logging._levelToName.copy()
            self.logger_states = logger_states = {}
            dla name w saved_loggers:
                logger_states[name] = getattr(saved_loggers[name],
                                              'disabled', Nic)
        w_końcu:
            logging._releaseLock()

        # Set two unused loggers
        self.logger1 = logging.getLogger("\xab\xd7\xbb")
        self.logger2 = logging.getLogger("\u013f\u00d6\u0047")

        self.root_logger = logging.getLogger("")
        self.original_logging_level = self.root_logger.getEffectiveLevel()

        self.stream = io.StringIO()
        self.root_logger.setLevel(logging.DEBUG)
        self.root_hdlr = logging.StreamHandler(self.stream)
        self.root_formatter = logging.Formatter(self.log_format)
        self.root_hdlr.setFormatter(self.root_formatter)
        jeżeli self.logger1.hasHandlers():
            hlist = self.logger1.handlers + self.root_logger.handlers
            podnieś AssertionError('Unexpected handlers: %s' % hlist)
        jeżeli self.logger2.hasHandlers():
            hlist = self.logger2.handlers + self.root_logger.handlers
            podnieś AssertionError('Unexpected handlers: %s' % hlist)
        self.root_logger.addHandler(self.root_hdlr)
        self.assertPrawda(self.logger1.hasHandlers())
        self.assertPrawda(self.logger2.hasHandlers())

    def tearDown(self):
        """Remove our logging stream, oraz restore the original logging
        level."""
        self.stream.close()
        self.root_logger.removeHandler(self.root_hdlr)
        dopóki self.root_logger.handlers:
            h = self.root_logger.handlers[0]
            self.root_logger.removeHandler(h)
            h.close()
        self.root_logger.setLevel(self.original_logging_level)
        logging._acquireLock()
        spróbuj:
            logging._levelToName.clear()
            logging._levelToName.update(self.saved_level_to_name)
            logging._nameToLevel.clear()
            logging._nameToLevel.update(self.saved_name_to_level)
            logging._handlers.clear()
            logging._handlers.update(self.saved_handlers)
            logging._handlerList[:] = self.saved_handler_list
            loggerDict = logging.getLogger().manager.loggerDict
            loggerDict.clear()
            loggerDict.update(self.saved_loggers)
            logger_states = self.logger_states
            dla name w self.logger_states:
                jeżeli logger_states[name] jest nie Nic:
                    self.saved_loggers[name].disabled = logger_states[name]
        w_końcu:
            logging._releaseLock()

    def assert_log_lines(self, expected_values, stream=Nic, pat=Nic):
        """Match the collected log lines against the regular expression
        self.expected_log_pat, oraz compare the extracted group values to
        the expected_values list of tuples."""
        stream = stream albo self.stream
        pat = re.compile(pat albo self.expected_log_pat)
        actual_lines = stream.getvalue().splitlines()
        self.assertEqual(len(actual_lines), len(expected_values))
        dla actual, expected w zip(actual_lines, expected_values):
            match = pat.search(actual)
            jeżeli nie match:
                self.fail("Log line does nie match expected pattern:\n" +
                            actual)
            self.assertEqual(tuple(match.groups()), expected)
        s = stream.read()
        jeżeli s:
            self.fail("Remaining output at end of log stream:\n" + s)

    def next_message(self):
        """Generate a message consisting solely of an auto-incrementing
        integer."""
        self.message_num += 1
        zwróć "%d" % self.message_num


klasa BuiltinLevelsTest(BaseTest):
    """Test builtin levels oraz their inheritance."""

    def test_flat(self):
        #Logging levels w a flat logger namespace.
        m = self.next_message

        ERR = logging.getLogger("ERR")
        ERR.setLevel(logging.ERROR)
        INF = logging.LoggerAdapter(logging.getLogger("INF"), {})
        INF.setLevel(logging.INFO)
        DEB = logging.getLogger("DEB")
        DEB.setLevel(logging.DEBUG)

        # These should log.
        ERR.log(logging.CRITICAL, m())
        ERR.error(m())

        INF.log(logging.CRITICAL, m())
        INF.error(m())
        INF.warning(m())
        INF.info(m())

        DEB.log(logging.CRITICAL, m())
        DEB.error(m())
        DEB.warning(m())
        DEB.info(m())
        DEB.debug(m())

        # These should nie log.
        ERR.warning(m())
        ERR.info(m())
        ERR.debug(m())

        INF.debug(m())

        self.assert_log_lines([
            ('ERR', 'CRITICAL', '1'),
            ('ERR', 'ERROR', '2'),
            ('INF', 'CRITICAL', '3'),
            ('INF', 'ERROR', '4'),
            ('INF', 'WARNING', '5'),
            ('INF', 'INFO', '6'),
            ('DEB', 'CRITICAL', '7'),
            ('DEB', 'ERROR', '8'),
            ('DEB', 'WARNING', '9'),
            ('DEB', 'INFO', '10'),
            ('DEB', 'DEBUG', '11'),
        ])

    def test_nested_explicit(self):
        # Logging levels w a nested namespace, all explicitly set.
        m = self.next_message

        INF = logging.getLogger("INF")
        INF.setLevel(logging.INFO)
        INF_ERR  = logging.getLogger("INF.ERR")
        INF_ERR.setLevel(logging.ERROR)

        # These should log.
        INF_ERR.log(logging.CRITICAL, m())
        INF_ERR.error(m())

        # These should nie log.
        INF_ERR.warning(m())
        INF_ERR.info(m())
        INF_ERR.debug(m())

        self.assert_log_lines([
            ('INF.ERR', 'CRITICAL', '1'),
            ('INF.ERR', 'ERROR', '2'),
        ])

    def test_nested_inherited(self):
        #Logging levels w a nested namespace, inherited z parent loggers.
        m = self.next_message

        INF = logging.getLogger("INF")
        INF.setLevel(logging.INFO)
        INF_ERR  = logging.getLogger("INF.ERR")
        INF_ERR.setLevel(logging.ERROR)
        INF_UNDEF = logging.getLogger("INF.UNDEF")
        INF_ERR_UNDEF = logging.getLogger("INF.ERR.UNDEF")
        UNDEF = logging.getLogger("UNDEF")

        # These should log.
        INF_UNDEF.log(logging.CRITICAL, m())
        INF_UNDEF.error(m())
        INF_UNDEF.warning(m())
        INF_UNDEF.info(m())
        INF_ERR_UNDEF.log(logging.CRITICAL, m())
        INF_ERR_UNDEF.error(m())

        # These should nie log.
        INF_UNDEF.debug(m())
        INF_ERR_UNDEF.warning(m())
        INF_ERR_UNDEF.info(m())
        INF_ERR_UNDEF.debug(m())

        self.assert_log_lines([
            ('INF.UNDEF', 'CRITICAL', '1'),
            ('INF.UNDEF', 'ERROR', '2'),
            ('INF.UNDEF', 'WARNING', '3'),
            ('INF.UNDEF', 'INFO', '4'),
            ('INF.ERR.UNDEF', 'CRITICAL', '5'),
            ('INF.ERR.UNDEF', 'ERROR', '6'),
        ])

    def test_nested_with_virtual_parent(self):
        # Logging levels when some parent does nie exist yet.
        m = self.next_message

        INF = logging.getLogger("INF")
        GRANDCHILD = logging.getLogger("INF.BADPARENT.UNDEF")
        CHILD = logging.getLogger("INF.BADPARENT")
        INF.setLevel(logging.INFO)

        # These should log.
        GRANDCHILD.log(logging.FATAL, m())
        GRANDCHILD.info(m())
        CHILD.log(logging.FATAL, m())
        CHILD.info(m())

        # These should nie log.
        GRANDCHILD.debug(m())
        CHILD.debug(m())

        self.assert_log_lines([
            ('INF.BADPARENT.UNDEF', 'CRITICAL', '1'),
            ('INF.BADPARENT.UNDEF', 'INFO', '2'),
            ('INF.BADPARENT', 'CRITICAL', '3'),
            ('INF.BADPARENT', 'INFO', '4'),
        ])

    def test_regression_22386(self):
        """See issue #22386 dla more information."""
        self.assertEqual(logging.getLevelName('INFO'), logging.INFO)
        self.assertEqual(logging.getLevelName(logging.INFO), 'INFO')

klasa BasicFilterTest(BaseTest):

    """Test the bundled Filter class."""

    def test_filter(self):
        # Only messages satisfying the specified criteria dalej through the
        #  filter.
        filter_ = logging.Filter("spam.eggs")
        handler = self.root_logger.handlers[0]
        spróbuj:
            handler.addFilter(filter_)
            spam = logging.getLogger("spam")
            spam_eggs = logging.getLogger("spam.eggs")
            spam_eggs_fish = logging.getLogger("spam.eggs.fish")
            spam_bakedbeans = logging.getLogger("spam.bakedbeans")

            spam.info(self.next_message())
            spam_eggs.info(self.next_message())  # Good.
            spam_eggs_fish.info(self.next_message())  # Good.
            spam_bakedbeans.info(self.next_message())

            self.assert_log_lines([
                ('spam.eggs', 'INFO', '2'),
                ('spam.eggs.fish', 'INFO', '3'),
            ])
        w_końcu:
            handler.removeFilter(filter_)

    def test_callable_filter(self):
        # Only messages satisfying the specified criteria dalej through the
        #  filter.

        def filterfunc(record):
            parts = record.name.split('.')
            prefix = '.'.join(parts[:2])
            zwróć prefix == 'spam.eggs'

        handler = self.root_logger.handlers[0]
        spróbuj:
            handler.addFilter(filterfunc)
            spam = logging.getLogger("spam")
            spam_eggs = logging.getLogger("spam.eggs")
            spam_eggs_fish = logging.getLogger("spam.eggs.fish")
            spam_bakedbeans = logging.getLogger("spam.bakedbeans")

            spam.info(self.next_message())
            spam_eggs.info(self.next_message())  # Good.
            spam_eggs_fish.info(self.next_message())  # Good.
            spam_bakedbeans.info(self.next_message())

            self.assert_log_lines([
                ('spam.eggs', 'INFO', '2'),
                ('spam.eggs.fish', 'INFO', '3'),
            ])
        w_końcu:
            handler.removeFilter(filterfunc)

    def test_empty_filter(self):
        f = logging.Filter()
        r = logging.makeLogRecord({'name': 'spam.eggs'})
        self.assertPrawda(f.filter(r))

#
#   First, we define our levels. There can be jako many jako you want - the only
#     limitations are that they should be integers, the lowest should be > 0 oraz
#   larger values mean less information being logged. If you need specific
#   level values which do nie fit into these limitations, you can use a
#   mapping dictionary to convert between your application levels oraz the
#   logging system.
#
SILENT      = 120
TACITURN    = 119
TERSE       = 118
EFFUSIVE    = 117
SOCIABLE    = 116
VERBOSE     = 115
TALKATIVE   = 114
GARRULOUS   = 113
CHATTERBOX  = 112
BORING      = 111

LEVEL_RANGE = range(BORING, SILENT + 1)

#
#   Next, we define names dla our levels. You don't need to do this - w which
#   case the system will use "Level n" to denote the text dla the level.
#
my_logging_levels = {
    SILENT      : 'Silent',
    TACITURN    : 'Taciturn',
    TERSE       : 'Terse',
    EFFUSIVE    : 'Effusive',
    SOCIABLE    : 'Sociable',
    VERBOSE     : 'Verbose',
    TALKATIVE   : 'Talkative',
    GARRULOUS   : 'Garrulous',
    CHATTERBOX  : 'Chatterbox',
    BORING      : 'Boring',
}

klasa GarrulousFilter(logging.Filter):

    """A filter which blocks garrulous messages."""

    def filter(self, record):
        zwróć record.levelno != GARRULOUS

klasa VerySpecificFilter(logging.Filter):

    """A filter which blocks sociable oraz taciturn messages."""

    def filter(self, record):
        zwróć record.levelno nie w [SOCIABLE, TACITURN]


klasa CustomLevelsAndFiltersTest(BaseTest):

    """Test various filtering possibilities przy custom logging levels."""

    # Skip the logger name group.
    expected_log_pat = r"^[\w.]+ -> (\w+): (\d+)$"

    def setUp(self):
        BaseTest.setUp(self)
        dla k, v w my_logging_levels.items():
            logging.addLevelName(k, v)

    def log_at_all_levels(self, logger):
        dla lvl w LEVEL_RANGE:
            logger.log(lvl, self.next_message())

    def test_logger_filter(self):
        # Filter at logger level.
        self.root_logger.setLevel(VERBOSE)
        # Levels >= 'Verbose' are good.
        self.log_at_all_levels(self.root_logger)
        self.assert_log_lines([
            ('Verbose', '5'),
            ('Sociable', '6'),
            ('Effusive', '7'),
            ('Terse', '8'),
            ('Taciturn', '9'),
            ('Silent', '10'),
        ])

    def test_handler_filter(self):
        # Filter at handler level.
        self.root_logger.handlers[0].setLevel(SOCIABLE)
        spróbuj:
            # Levels >= 'Sociable' are good.
            self.log_at_all_levels(self.root_logger)
            self.assert_log_lines([
                ('Sociable', '6'),
                ('Effusive', '7'),
                ('Terse', '8'),
                ('Taciturn', '9'),
                ('Silent', '10'),
            ])
        w_końcu:
            self.root_logger.handlers[0].setLevel(logging.NOTSET)

    def test_specific_filters(self):
        # Set a specific filter object on the handler, oraz then add another
        #  filter object on the logger itself.
        handler = self.root_logger.handlers[0]
        specific_filter = Nic
        garr = GarrulousFilter()
        handler.addFilter(garr)
        spróbuj:
            self.log_at_all_levels(self.root_logger)
            first_lines = [
                # Notice how 'Garrulous' jest missing
                ('Boring', '1'),
                ('Chatterbox', '2'),
                ('Talkative', '4'),
                ('Verbose', '5'),
                ('Sociable', '6'),
                ('Effusive', '7'),
                ('Terse', '8'),
                ('Taciturn', '9'),
                ('Silent', '10'),
            ]
            self.assert_log_lines(first_lines)

            specific_filter = VerySpecificFilter()
            self.root_logger.addFilter(specific_filter)
            self.log_at_all_levels(self.root_logger)
            self.assert_log_lines(first_lines + [
                # Not only 'Garrulous' jest still missing, but also 'Sociable'
                # oraz 'Taciturn'
                ('Boring', '11'),
                ('Chatterbox', '12'),
                ('Talkative', '14'),
                ('Verbose', '15'),
                ('Effusive', '17'),
                ('Terse', '18'),
                ('Silent', '20'),
        ])
        w_końcu:
            jeżeli specific_filter:
                self.root_logger.removeFilter(specific_filter)
            handler.removeFilter(garr)


klasa HandlerTest(BaseTest):
    def test_name(self):
        h = logging.Handler()
        h.name = 'generic'
        self.assertEqual(h.name, 'generic')
        h.name = 'anothergeneric'
        self.assertEqual(h.name, 'anothergeneric')
        self.assertRaises(NotImplementedError, h.emit, Nic)

    def test_builtin_handlers(self):
        # We can't actually *use* too many handlers w the tests,
        # but we can try instantiating them przy various options
        jeżeli sys.platform w ('linux', 'darwin'):
            dla existing w (Prawda, Nieprawda):
                fd, fn = tempfile.mkstemp()
                os.close(fd)
                jeżeli nie existing:
                    os.unlink(fn)
                h = logging.handlers.WatchedFileHandler(fn, delay=Prawda)
                jeżeli existing:
                    dev, ino = h.dev, h.ino
                    self.assertEqual(dev, -1)
                    self.assertEqual(ino, -1)
                    r = logging.makeLogRecord({'msg': 'Test'})
                    h.handle(r)
                    # Now remove the file.
                    os.unlink(fn)
                    self.assertNieprawda(os.path.exists(fn))
                    # The next call should recreate the file.
                    h.handle(r)
                    self.assertPrawda(os.path.exists(fn))
                inaczej:
                    self.assertEqual(h.dev, -1)
                    self.assertEqual(h.ino, -1)
                h.close()
                jeżeli existing:
                    os.unlink(fn)
            jeżeli sys.platform == 'darwin':
                sockname = '/var/run/syslog'
            inaczej:
                sockname = '/dev/log'
            spróbuj:
                h = logging.handlers.SysLogHandler(sockname)
                self.assertEqual(h.facility, h.LOG_USER)
                self.assertPrawda(h.unixsocket)
                h.close()
            wyjąwszy OSError: # syslogd might nie be available
                dalej
        dla method w ('GET', 'POST', 'PUT'):
            jeżeli method == 'PUT':
                self.assertRaises(ValueError, logging.handlers.HTTPHandler,
                                  'localhost', '/log', method)
            inaczej:
                h = logging.handlers.HTTPHandler('localhost', '/log', method)
                h.close()
        h = logging.handlers.BufferingHandler(0)
        r = logging.makeLogRecord({})
        self.assertPrawda(h.shouldFlush(r))
        h.close()
        h = logging.handlers.BufferingHandler(1)
        self.assertNieprawda(h.shouldFlush(r))
        h.close()

    @unittest.skipIf(os.name == 'nt', 'WatchedFileHandler nie appropriate dla Windows.')
    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_race(self):
        # Issue #14632 refers.
        def remove_loop(fname, tries):
            dla _ w range(tries):
                spróbuj:
                    os.unlink(fname)
                    self.deletion_time = time.time()
                wyjąwszy OSError:
                    dalej
                time.sleep(0.004 * random.randint(0, 4))

        del_count = 500
        log_count = 500

        self.handle_time = Nic
        self.deletion_time = Nic

        dla delay w (Nieprawda, Prawda):
            fd, fn = tempfile.mkstemp('.log', 'test_logging-3-')
            os.close(fd)
            remover = threading.Thread(target=remove_loop, args=(fn, del_count))
            remover.daemon = Prawda
            remover.start()
            h = logging.handlers.WatchedFileHandler(fn, delay=delay)
            f = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
            h.setFormatter(f)
            spróbuj:
                dla _ w range(log_count):
                    time.sleep(0.005)
                    r = logging.makeLogRecord({'msg': 'testing' })
                    spróbuj:
                        self.handle_time = time.time()
                        h.handle(r)
                    wyjąwszy Exception:
                        print('Deleted at %s, '
                              'opened at %s' % (self.deletion_time,
                                                self.handle_time))
                        podnieś
            w_końcu:
                remover.join()
                h.close()
                jeżeli os.path.exists(fn):
                    os.unlink(fn)


klasa BadStream(object):
    def write(self, data):
        podnieś RuntimeError('deliberate mistake')

klasa TestStreamHandler(logging.StreamHandler):
    def handleError(self, record):
        self.error_record = record

klasa StreamHandlerTest(BaseTest):
    def test_error_handling(self):
        h = TestStreamHandler(BadStream())
        r = logging.makeLogRecord({})
        old_raise = logging.raiseExceptions

        spróbuj:
            h.handle(r)
            self.assertIs(h.error_record, r)

            h = logging.StreamHandler(BadStream())
            przy support.captured_stderr() jako stderr:
                h.handle(r)
                msg = '\nRuntimeError: deliberate mistake\n'
                self.assertIn(msg, stderr.getvalue())

            logging.raiseExceptions = Nieprawda
            przy support.captured_stderr() jako stderr:
                h.handle(r)
                self.assertEqual('', stderr.getvalue())
        w_końcu:
            logging.raiseExceptions = old_raise

# -- The following section could be moved into a server_helper.py module
# -- jeżeli it proves to be of wider utility than just test_logging

jeżeli threading:
    klasa TestSMTPServer(smtpd.SMTPServer):
        """
        This klasa implements a test SMTP server.

        :param addr: A (host, port) tuple which the server listens on.
                     You can specify a port value of zero: the server's
                     *port* attribute will hold the actual port number
                     used, which can be used w client connections.
        :param handler: A callable which will be called to process
                        incoming messages. The handler will be dalejed
                        the client address tuple, who the message jest from,
                        a list of recipients oraz the message data.
        :param poll_interval: The interval, w seconds, used w the underlying
                              :func:`select` albo :func:`poll` call by
                              :func:`asyncore.loop`.
        :param sockmap: A dictionary which will be used to hold
                        :class:`asyncore.dispatcher` instances used by
                        :func:`asyncore.loop`. This avoids changing the
                        :mod:`asyncore` module's global state.
        """

        def __init__(self, addr, handler, poll_interval, sockmap):
            smtpd.SMTPServer.__init__(self, addr, Nic, map=sockmap,
                                      decode_data=Prawda)
            self.port = self.socket.getsockname()[1]
            self._handler = handler
            self._thread = Nic
            self.poll_interval = poll_interval

        def process_message(self, peer, mailfrom, rcpttos, data):
            """
            Delegates to the handler dalejed w to the server's constructor.

            Typically, this will be a test case method.
            :param peer: The client (host, port) tuple.
            :param mailfrom: The address of the sender.
            :param rcpttos: The addresses of the recipients.
            :param data: The message.
            """
            self._handler(peer, mailfrom, rcpttos, data)

        def start(self):
            """
            Start the server running on a separate daemon thread.
            """
            self._thread = t = threading.Thread(target=self.serve_forever,
                                                args=(self.poll_interval,))
            t.setDaemon(Prawda)
            t.start()

        def serve_forever(self, poll_interval):
            """
            Run the :mod:`asyncore` loop until normal termination
            conditions arise.
            :param poll_interval: The interval, w seconds, used w the underlying
                                  :func:`select` albo :func:`poll` call by
                                  :func:`asyncore.loop`.
            """
            spróbuj:
                asyncore.loop(poll_interval, map=self._map)
            wyjąwszy OSError:
                # On FreeBSD 8, closing the server repeatably
                # podnieśs this error. We swallow it jeżeli the
                # server has been closed.
                jeżeli self.connected albo self.accepting:
                    podnieś

        def stop(self, timeout=Nic):
            """
            Stop the thread by closing the server instance.
            Wait dla the server thread to terminate.

            :param timeout: How long to wait dla the server thread
                            to terminate.
            """
            self.close()
            self._thread.join(timeout)
            self._thread = Nic

    klasa ControlMixin(object):
        """
        This mixin jest used to start a server on a separate thread, oraz
        shut it down programmatically. Request handling jest simplified - instead
        of needing to derive a suitable RequestHandler subclass, you just
        provide a callable which will be dalejed each received request to be
        processed.

        :param handler: A handler callable which will be called przy a
                        single parameter - the request - w order to
                        process the request. This handler jest called on the
                        server thread, effectively meaning that requests are
                        processed serially. While nie quite Web scale ;-),
                        this should be fine dla testing applications.
        :param poll_interval: The polling interval w seconds.
        """
        def __init__(self, handler, poll_interval):
            self._thread = Nic
            self.poll_interval = poll_interval
            self._handler = handler
            self.ready = threading.Event()

        def start(self):
            """
            Create a daemon thread to run the server, oraz start it.
            """
            self._thread = t = threading.Thread(target=self.serve_forever,
                                                args=(self.poll_interval,))
            t.setDaemon(Prawda)
            t.start()

        def serve_forever(self, poll_interval):
            """
            Run the server. Set the ready flag before entering the
            service loop.
            """
            self.ready.set()
            super(ControlMixin, self).serve_forever(poll_interval)

        def stop(self, timeout=Nic):
            """
            Tell the server thread to stop, oraz wait dla it to do so.

            :param timeout: How long to wait dla the server thread
                            to terminate.
            """
            self.shutdown()
            jeżeli self._thread jest nie Nic:
                self._thread.join(timeout)
                self._thread = Nic
            self.server_close()
            self.ready.clear()

    klasa TestHTTPServer(ControlMixin, HTTPServer):
        """
        An HTTP server which jest controllable using :class:`ControlMixin`.

        :param addr: A tuple przy the IP address oraz port to listen on.
        :param handler: A handler callable which will be called przy a
                        single parameter - the request - w order to
                        process the request.
        :param poll_interval: The polling interval w seconds.
        :param log: Pass ``Prawda`` to enable log messages.
        """
        def __init__(self, addr, handler, poll_interval=0.5,
                     log=Nieprawda, sslctx=Nic):
            klasa DelegatingHTTPRequestHandler(BaseHTTPRequestHandler):
                def __getattr__(self, name, default=Nic):
                    jeżeli name.startswith('do_'):
                        zwróć self.process_request
                    podnieś AttributeError(name)

                def process_request(self):
                    self.server._handler(self)

                def log_message(self, format, *args):
                    jeżeli log:
                        super(DelegatingHTTPRequestHandler,
                              self).log_message(format, *args)
            HTTPServer.__init__(self, addr, DelegatingHTTPRequestHandler)
            ControlMixin.__init__(self, handler, poll_interval)
            self.sslctx = sslctx

        def get_request(self):
            spróbuj:
                sock, addr = self.socket.accept()
                jeżeli self.sslctx:
                    sock = self.sslctx.wrap_socket(sock, server_side=Prawda)
            wyjąwszy OSError jako e:
                # socket errors are silenced by the caller, print them here
                sys.stderr.write("Got an error:\n%s\n" % e)
                podnieś
            zwróć sock, addr

    klasa TestTCPServer(ControlMixin, ThreadingTCPServer):
        """
        A TCP server which jest controllable using :class:`ControlMixin`.

        :param addr: A tuple przy the IP address oraz port to listen on.
        :param handler: A handler callable which will be called przy a single
                        parameter - the request - w order to process the request.
        :param poll_interval: The polling interval w seconds.
        :bind_and_activate: If Prawda (the default), binds the server oraz starts it
                            listening. If Nieprawda, you need to call
                            :meth:`server_bind` oraz :meth:`server_activate` at
                            some later time before calling :meth:`start`, so that
                            the server will set up the socket oraz listen on it.
        """

        allow_reuse_address = Prawda

        def __init__(self, addr, handler, poll_interval=0.5,
                     bind_and_activate=Prawda):
            klasa DelegatingTCPRequestHandler(StreamRequestHandler):

                def handle(self):
                    self.server._handler(self)
            ThreadingTCPServer.__init__(self, addr, DelegatingTCPRequestHandler,
                                        bind_and_activate)
            ControlMixin.__init__(self, handler, poll_interval)

        def server_bind(self):
            super(TestTCPServer, self).server_bind()
            self.port = self.socket.getsockname()[1]

    klasa TestUDPServer(ControlMixin, ThreadingUDPServer):
        """
        A UDP server which jest controllable using :class:`ControlMixin`.

        :param addr: A tuple przy the IP address oraz port to listen on.
        :param handler: A handler callable which will be called przy a
                        single parameter - the request - w order to
                        process the request.
        :param poll_interval: The polling interval dla shutdown requests,
                              w seconds.
        :bind_and_activate: If Prawda (the default), binds the server oraz
                            starts it listening. If Nieprawda, you need to
                            call :meth:`server_bind` oraz
                            :meth:`server_activate` at some later time
                            before calling :meth:`start`, so that the server will
                            set up the socket oraz listen on it.
        """
        def __init__(self, addr, handler, poll_interval=0.5,
                     bind_and_activate=Prawda):
            klasa DelegatingUDPRequestHandler(DatagramRequestHandler):

                def handle(self):
                    self.server._handler(self)

                def finish(self):
                    data = self.wfile.getvalue()
                    jeżeli data:
                        spróbuj:
                            super(DelegatingUDPRequestHandler, self).finish()
                        wyjąwszy OSError:
                            jeżeli nie self.server._closed:
                                podnieś

            ThreadingUDPServer.__init__(self, addr,
                                        DelegatingUDPRequestHandler,
                                        bind_and_activate)
            ControlMixin.__init__(self, handler, poll_interval)
            self._closed = Nieprawda

        def server_bind(self):
            super(TestUDPServer, self).server_bind()
            self.port = self.socket.getsockname()[1]

        def server_close(self):
            super(TestUDPServer, self).server_close()
            self._closed = Prawda

    jeżeli hasattr(socket, "AF_UNIX"):
        klasa TestUnixStreamServer(TestTCPServer):
            address_family = socket.AF_UNIX

        klasa TestUnixDatagramServer(TestUDPServer):
            address_family = socket.AF_UNIX

# - end of server_helper section

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SMTPHandlerTest(BaseTest):
    TIMEOUT = 8.0
    def test_basic(self):
        sockmap = {}
        server = TestSMTPServer((support.HOST, 0), self.process_message, 0.001,
                                sockmap)
        server.start()
        addr = (support.HOST, server.port)
        h = logging.handlers.SMTPHandler(addr, 'me', 'you', 'Log',
                                         timeout=self.TIMEOUT)
        self.assertEqual(h.toaddrs, ['you'])
        self.messages = []
        r = logging.makeLogRecord({'msg': 'Hello'})
        self.handled = threading.Event()
        h.handle(r)
        self.handled.wait(self.TIMEOUT)  # 14314: don't wait forever
        server.stop()
        self.assertPrawda(self.handled.is_set())
        self.assertEqual(len(self.messages), 1)
        peer, mailfrom, rcpttos, data = self.messages[0]
        self.assertEqual(mailfrom, 'me')
        self.assertEqual(rcpttos, ['you'])
        self.assertIn('\nSubject: Log\n', data)
        self.assertPrawda(data.endswith('\n\nHello'))
        h.close()

    def process_message(self, *args):
        self.messages.append(args)
        self.handled.set()

klasa MemoryHandlerTest(BaseTest):

    """Tests dla the MemoryHandler."""

    # Do nie bother przy a logger name group.
    expected_log_pat = r"^[\w.]+ -> (\w+): (\d+)$"

    def setUp(self):
        BaseTest.setUp(self)
        self.mem_hdlr = logging.handlers.MemoryHandler(10, logging.WARNING,
                                                        self.root_hdlr)
        self.mem_logger = logging.getLogger('mem')
        self.mem_logger.propagate = 0
        self.mem_logger.addHandler(self.mem_hdlr)

    def tearDown(self):
        self.mem_hdlr.close()
        BaseTest.tearDown(self)

    def test_flush(self):
        # The memory handler flushes to its target handler based on specific
        #  criteria (message count oraz message level).
        self.mem_logger.debug(self.next_message())
        self.assert_log_lines([])
        self.mem_logger.info(self.next_message())
        self.assert_log_lines([])
        # This will flush because the level jest >= logging.WARNING
        self.mem_logger.warning(self.next_message())
        lines = [
            ('DEBUG', '1'),
            ('INFO', '2'),
            ('WARNING', '3'),
        ]
        self.assert_log_lines(lines)
        dla n w (4, 14):
            dla i w range(9):
                self.mem_logger.debug(self.next_message())
            self.assert_log_lines(lines)
            # This will flush because it's the 10th message since the last
            #  flush.
            self.mem_logger.debug(self.next_message())
            lines = lines + [('DEBUG', str(i)) dla i w range(n, n + 10)]
            self.assert_log_lines(lines)

        self.mem_logger.debug(self.next_message())
        self.assert_log_lines(lines)


klasa ExceptionFormatter(logging.Formatter):
    """A special exception formatter."""
    def formatException(self, ei):
        zwróć "Got a [%s]" % ei[0].__name__


klasa ConfigFileTest(BaseTest):

    """Reading logging config z a .ini-style config file."""

    expected_log_pat = r"^(\w+) \+\+ (\w+)$"

    # config0 jest a standard configuration.
    config0 = """
    [loggers]
    keys=root

    [handlers]
    keys=hand1

    [formatters]
    keys=form1

    [logger_root]
    level=WARNING
    handlers=hand1

    [handler_hand1]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stdout,)

    [formatter_form1]
    format=%(levelname)s ++ %(message)s
    datefmt=
    """

    # config1 adds a little to the standard configuration.
    config1 = """
    [loggers]
    keys=root,parser

    [handlers]
    keys=hand1

    [formatters]
    keys=form1

    [logger_root]
    level=WARNING
    handlers=

    [logger_parser]
    level=DEBUG
    handlers=hand1
    propagate=1
    qualname=compiler.parser

    [handler_hand1]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stdout,)

    [formatter_form1]
    format=%(levelname)s ++ %(message)s
    datefmt=
    """

    # config1a moves the handler to the root.
    config1a = """
    [loggers]
    keys=root,parser

    [handlers]
    keys=hand1

    [formatters]
    keys=form1

    [logger_root]
    level=WARNING
    handlers=hand1

    [logger_parser]
    level=DEBUG
    handlers=
    propagate=1
    qualname=compiler.parser

    [handler_hand1]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stdout,)

    [formatter_form1]
    format=%(levelname)s ++ %(message)s
    datefmt=
    """

    # config2 has a subtle configuration error that should be reported
    config2 = config1.replace("sys.stdout", "sys.stbout")

    # config3 has a less subtle configuration error
    config3 = config1.replace("formatter=form1", "formatter=misspelled_name")

    # config4 specifies a custom formatter klasa to be loaded
    config4 = """
    [loggers]
    keys=root

    [handlers]
    keys=hand1

    [formatters]
    keys=form1

    [logger_root]
    level=NOTSET
    handlers=hand1

    [handler_hand1]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stdout,)

    [formatter_form1]
    class=""" + __name__ + """.ExceptionFormatter
    format=%(levelname)s:%(name)s:%(message)s
    datefmt=
    """

    # config5 specifies a custom handler klasa to be loaded
    config5 = config1.replace('class=StreamHandler', 'class=logging.StreamHandler')

    # config6 uses ', ' delimiters w the handlers oraz formatters sections
    config6 = """
    [loggers]
    keys=root,parser

    [handlers]
    keys=hand1, hand2

    [formatters]
    keys=form1, form2

    [logger_root]
    level=WARNING
    handlers=

    [logger_parser]
    level=DEBUG
    handlers=hand1
    propagate=1
    qualname=compiler.parser

    [handler_hand1]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stdout,)

    [handler_hand2]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stderr,)

    [formatter_form1]
    format=%(levelname)s ++ %(message)s
    datefmt=

    [formatter_form2]
    format=%(message)s
    datefmt=
    """

    # config7 adds a compiler logger.
    config7 = """
    [loggers]
    keys=root,parser,compiler

    [handlers]
    keys=hand1

    [formatters]
    keys=form1

    [logger_root]
    level=WARNING
    handlers=hand1

    [logger_compiler]
    level=DEBUG
    handlers=
    propagate=1
    qualname=compiler

    [logger_parser]
    level=DEBUG
    handlers=
    propagate=1
    qualname=compiler.parser

    [handler_hand1]
    class=StreamHandler
    level=NOTSET
    formatter=form1
    args=(sys.stdout,)

    [formatter_form1]
    format=%(levelname)s ++ %(message)s
    datefmt=
    """

    disable_test = """
    [loggers]
    keys=root

    [handlers]
    keys=screen

    [formatters]
    keys=

    [logger_root]
    level=DEBUG
    handlers=screen

    [handler_screen]
    level=DEBUG
    class=StreamHandler
    args=(sys.stdout,)
    formatter=
    """

    def apply_config(self, conf, **kwargs):
        file = io.StringIO(textwrap.dedent(conf))
        logging.config.fileConfig(file, **kwargs)

    def test_config0_ok(self):
        # A simple config file which overrides the default settings.
        przy support.captured_stdout() jako output:
            self.apply_config(self.config0)
            logger = logging.getLogger()
            # Won't output anything
            logger.info(self.next_message())
            # Outputs a message
            logger.error(self.next_message())
            self.assert_log_lines([
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config0_using_cp_ok(self):
        # A simple config file which overrides the default settings.
        przy support.captured_stdout() jako output:
            file = io.StringIO(textwrap.dedent(self.config0))
            cp = configparser.ConfigParser()
            cp.read_file(file)
            logging.config.fileConfig(cp)
            logger = logging.getLogger()
            # Won't output anything
            logger.info(self.next_message())
            # Outputs a message
            logger.error(self.next_message())
            self.assert_log_lines([
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config1_ok(self, config=config1):
        # A config file defining a sub-parser jako well.
        przy support.captured_stdout() jako output:
            self.apply_config(config)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config2_failure(self):
        # A simple config file which overrides the default settings.
        self.assertRaises(Exception, self.apply_config, self.config2)

    def test_config3_failure(self):
        # A simple config file which overrides the default settings.
        self.assertRaises(Exception, self.apply_config, self.config3)

    def test_config4_ok(self):
        # A config file specifying a custom formatter class.
        przy support.captured_stdout() jako output:
            self.apply_config(self.config4)
            logger = logging.getLogger()
            spróbuj:
                podnieś RuntimeError()
            wyjąwszy RuntimeError:
                logging.exception("just testing")
            sys.stdout.seek(0)
            self.assertEqual(output.getvalue(),
                "ERROR:root:just testing\nGot a [RuntimeError]\n")
            # Original logger output jest empty
            self.assert_log_lines([])

    def test_config5_ok(self):
        self.test_config1_ok(config=self.config5)

    def test_config6_ok(self):
        self.test_config1_ok(config=self.config6)

    def test_config7_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config1a)
            logger = logging.getLogger("compiler.parser")
            # See issue #11424. compiler-hyphenated sorts
            # between compiler oraz compiler.xyz oraz this
            # was preventing compiler.xyz z being included
            # w the child loggers of compiler because of an
            # overzealous loop termination condition.
            hyphenated = logging.getLogger('compiler-hyphenated')
            # All will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            hyphenated.critical(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
                ('CRITICAL', '3'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])
        przy support.captured_stdout() jako output:
            self.apply_config(self.config7)
            logger = logging.getLogger("compiler.parser")
            self.assertNieprawda(logger.disabled)
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            logger = logging.getLogger("compiler.lexer")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            # Will nie appear
            hyphenated.critical(self.next_message())
            self.assert_log_lines([
                ('INFO', '4'),
                ('ERROR', '5'),
                ('INFO', '6'),
                ('ERROR', '7'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_logger_disabling(self):
        self.apply_config(self.disable_test)
        logger = logging.getLogger('some_pristine_logger')
        self.assertNieprawda(logger.disabled)
        self.apply_config(self.disable_test)
        self.assertPrawda(logger.disabled)
        self.apply_config(self.disable_test, disable_existing_loggers=Nieprawda)
        self.assertNieprawda(logger.disabled)


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SocketHandlerTest(BaseTest):

    """Test dla SocketHandler objects."""

    jeżeli threading:
        server_class = TestTCPServer
        address = ('localhost', 0)

    def setUp(self):
        """Set up a TCP server to receive log messages, oraz a SocketHandler
        pointing to that server's address oraz port."""
        BaseTest.setUp(self)
        self.server = server = self.server_class(self.address,
                                                 self.handle_socket, 0.01)
        server.start()
        server.ready.wait()
        hcls = logging.handlers.SocketHandler
        jeżeli isinstance(server.server_address, tuple):
            self.sock_hdlr = hcls('localhost', server.port)
        inaczej:
            self.sock_hdlr = hcls(server.server_address, Nic)
        self.log_output = ''
        self.root_logger.removeHandler(self.root_logger.handlers[0])
        self.root_logger.addHandler(self.sock_hdlr)
        self.handled = threading.Semaphore(0)

    def tearDown(self):
        """Shutdown the TCP server."""
        spróbuj:
            self.server.stop(2.0)
            self.root_logger.removeHandler(self.sock_hdlr)
            self.sock_hdlr.close()
        w_końcu:
            BaseTest.tearDown(self)

    def handle_socket(self, request):
        conn = request.connection
        dopóki Prawda:
            chunk = conn.recv(4)
            jeżeli len(chunk) < 4:
                przerwij
            slen = struct.unpack(">L", chunk)[0]
            chunk = conn.recv(slen)
            dopóki len(chunk) < slen:
                chunk = chunk + conn.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            self.log_output += record.msg + '\n'
            self.handled.release()

    def test_output(self):
        # The log message sent to the SocketHandler jest properly received.
        logger = logging.getLogger("tcp")
        logger.error("spam")
        self.handled.acquire()
        logger.debug("eggs")
        self.handled.acquire()
        self.assertEqual(self.log_output, "spam\neggs\n")

    def test_noserver(self):
        # Avoid timing-related failures due to SocketHandler's own hard-wired
        # one-second timeout on socket.create_connection() (issue #16264).
        self.sock_hdlr.retryStart = 2.5
        # Kill the server
        self.server.stop(2.0)
        # The logging call should try to connect, which should fail
        spróbuj:
            podnieś RuntimeError('Deliberate mistake')
        wyjąwszy RuntimeError:
            self.root_logger.exception('Never sent')
        self.root_logger.error('Never sent, either')
        now = time.time()
        self.assertGreater(self.sock_hdlr.retryTime, now)
        time.sleep(self.sock_hdlr.retryTime - now + 0.001)
        self.root_logger.error('Nor this')

def _get_temp_domain_socket():
    fd, fn = tempfile.mkstemp(prefix='test_logging_', suffix='.sock')
    os.close(fd)
    # just need a name - file can't be present, albo we'll get an
    # 'address already w use' error.
    os.remove(fn)
    zwróć fn

@unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets required")
@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa UnixSocketHandlerTest(SocketHandlerTest):

    """Test dla SocketHandler przy unix sockets."""

    jeżeli threading oraz hasattr(socket, "AF_UNIX"):
        server_class = TestUnixStreamServer

    def setUp(self):
        # override the definition w the base class
        self.address = _get_temp_domain_socket()
        SocketHandlerTest.setUp(self)

    def tearDown(self):
        SocketHandlerTest.tearDown(self)
        os.remove(self.address)

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa DatagramHandlerTest(BaseTest):

    """Test dla DatagramHandler."""

    jeżeli threading:
        server_class = TestUDPServer
        address = ('localhost', 0)

    def setUp(self):
        """Set up a UDP server to receive log messages, oraz a DatagramHandler
        pointing to that server's address oraz port."""
        BaseTest.setUp(self)
        self.server = server = self.server_class(self.address,
                                                 self.handle_datagram, 0.01)
        server.start()
        server.ready.wait()
        hcls = logging.handlers.DatagramHandler
        jeżeli isinstance(server.server_address, tuple):
            self.sock_hdlr = hcls('localhost', server.port)
        inaczej:
            self.sock_hdlr = hcls(server.server_address, Nic)
        self.log_output = ''
        self.root_logger.removeHandler(self.root_logger.handlers[0])
        self.root_logger.addHandler(self.sock_hdlr)
        self.handled = threading.Event()

    def tearDown(self):
        """Shutdown the UDP server."""
        spróbuj:
            self.server.stop(2.0)
            self.root_logger.removeHandler(self.sock_hdlr)
            self.sock_hdlr.close()
        w_końcu:
            BaseTest.tearDown(self)

    def handle_datagram(self, request):
        slen = struct.pack('>L', 0) # length of prefix
        packet = request.packet[len(slen):]
        obj = pickle.loads(packet)
        record = logging.makeLogRecord(obj)
        self.log_output += record.msg + '\n'
        self.handled.set()

    def test_output(self):
        # The log message sent to the DatagramHandler jest properly received.
        logger = logging.getLogger("udp")
        logger.error("spam")
        self.handled.wait()
        self.handled.clear()
        logger.error("eggs")
        self.handled.wait()
        self.assertEqual(self.log_output, "spam\neggs\n")

@unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets required")
@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa UnixDatagramHandlerTest(DatagramHandlerTest):

    """Test dla DatagramHandler using Unix sockets."""

    jeżeli threading oraz hasattr(socket, "AF_UNIX"):
        server_class = TestUnixDatagramServer

    def setUp(self):
        # override the definition w the base class
        self.address = _get_temp_domain_socket()
        DatagramHandlerTest.setUp(self)

    def tearDown(self):
        DatagramHandlerTest.tearDown(self)
        os.remove(self.address)

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SysLogHandlerTest(BaseTest):

    """Test dla SysLogHandler using UDP."""

    jeżeli threading:
        server_class = TestUDPServer
        address = ('localhost', 0)

    def setUp(self):
        """Set up a UDP server to receive log messages, oraz a SysLogHandler
        pointing to that server's address oraz port."""
        BaseTest.setUp(self)
        self.server = server = self.server_class(self.address,
                                                 self.handle_datagram, 0.01)
        server.start()
        server.ready.wait()
        hcls = logging.handlers.SysLogHandler
        jeżeli isinstance(server.server_address, tuple):
            self.sl_hdlr = hcls(('localhost', server.port))
        inaczej:
            self.sl_hdlr = hcls(server.server_address)
        self.log_output = ''
        self.root_logger.removeHandler(self.root_logger.handlers[0])
        self.root_logger.addHandler(self.sl_hdlr)
        self.handled = threading.Event()

    def tearDown(self):
        """Shutdown the UDP server."""
        spróbuj:
            self.server.stop(2.0)
            self.root_logger.removeHandler(self.sl_hdlr)
            self.sl_hdlr.close()
        w_końcu:
            BaseTest.tearDown(self)

    def handle_datagram(self, request):
        self.log_output = request.packet
        self.handled.set()

    def test_output(self):
        # The log message sent to the SysLogHandler jest properly received.
        logger = logging.getLogger("slh")
        logger.error("sp\xe4m")
        self.handled.wait()
        self.assertEqual(self.log_output, b'<11>sp\xc3\xa4m\x00')
        self.handled.clear()
        self.sl_hdlr.append_nul = Nieprawda
        logger.error("sp\xe4m")
        self.handled.wait()
        self.assertEqual(self.log_output, b'<11>sp\xc3\xa4m')
        self.handled.clear()
        self.sl_hdlr.ident = "h\xe4m-"
        logger.error("sp\xe4m")
        self.handled.wait()
        self.assertEqual(self.log_output, b'<11>h\xc3\xa4m-sp\xc3\xa4m')

@unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets required")
@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa UnixSysLogHandlerTest(SysLogHandlerTest):

    """Test dla SysLogHandler przy Unix sockets."""

    jeżeli threading oraz hasattr(socket, "AF_UNIX"):
        server_class = TestUnixDatagramServer

    def setUp(self):
        # override the definition w the base class
        self.address = _get_temp_domain_socket()
        SysLogHandlerTest.setUp(self)

    def tearDown(self):
        SysLogHandlerTest.tearDown(self)
        os.remove(self.address)

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa HTTPHandlerTest(BaseTest):
    """Test dla HTTPHandler."""

    def setUp(self):
        """Set up an HTTP server to receive log messages, oraz a HTTPHandler
        pointing to that server's address oraz port."""
        BaseTest.setUp(self)
        self.handled = threading.Event()

    def handle_request(self, request):
        self.command = request.command
        self.log_data = urlparse(request.path)
        jeżeli self.command == 'POST':
            spróbuj:
                rlen = int(request.headers['Content-Length'])
                self.post_data = request.rfile.read(rlen)
            wyjąwszy:
                self.post_data = Nic
        request.send_response(200)
        request.end_headers()
        self.handled.set()

    def test_output(self):
        # The log message sent to the HTTPHandler jest properly received.
        logger = logging.getLogger("http")
        root_logger = self.root_logger
        root_logger.removeHandler(self.root_logger.handlers[0])
        dla secure w (Nieprawda, Prawda):
            addr = ('localhost', 0)
            jeżeli secure:
                spróbuj:
                    zaimportuj ssl
                wyjąwszy ImportError:
                    sslctx = Nic
                inaczej:
                    here = os.path.dirname(__file__)
                    localhost_cert = os.path.join(here, "keycert.pem")
                    sslctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                    sslctx.load_cert_chain(localhost_cert)

                    context = ssl.create_default_context(cafile=localhost_cert)
            inaczej:
                sslctx = Nic
                context = Nic
            self.server = server = TestHTTPServer(addr, self.handle_request,
                                                    0.01, sslctx=sslctx)
            server.start()
            server.ready.wait()
            host = 'localhost:%d' % server.server_port
            secure_client = secure oraz sslctx
            self.h_hdlr = logging.handlers.HTTPHandler(host, '/frob',
                                                       secure=secure_client,
                                                       context=context)
            self.log_data = Nic
            root_logger.addHandler(self.h_hdlr)

            dla method w ('GET', 'POST'):
                self.h_hdlr.method = method
                self.handled.clear()
                msg = "sp\xe4m"
                logger.error(msg)
                self.handled.wait()
                self.assertEqual(self.log_data.path, '/frob')
                self.assertEqual(self.command, method)
                jeżeli method == 'GET':
                    d = parse_qs(self.log_data.query)
                inaczej:
                    d = parse_qs(self.post_data.decode('utf-8'))
                self.assertEqual(d['name'], ['http'])
                self.assertEqual(d['funcName'], ['test_output'])
                self.assertEqual(d['msg'], [msg])

            self.server.stop(2.0)
            self.root_logger.removeHandler(self.h_hdlr)
            self.h_hdlr.close()

klasa MemoryTest(BaseTest):

    """Test memory persistence of logger objects."""

    def setUp(self):
        """Create a dict to remember potentially destroyed objects."""
        BaseTest.setUp(self)
        self._survivors = {}

    def _watch_for_survival(self, *args):
        """Watch the given objects dla survival, by creating weakrefs to
        them."""
        dla obj w args:
            key = id(obj), repr(obj)
            self._survivors[key] = weakref.ref(obj)

    def _assertPrawdasurvival(self):
        """Assert that all objects watched dla survival have survived."""
        # Trigger cycle przerwijing.
        gc.collect()
        dead = []
        dla (id_, repr_), ref w self._survivors.items():
            jeżeli ref() jest Nic:
                dead.append(repr_)
        jeżeli dead:
            self.fail("%d objects should have survived "
                "but have been destroyed: %s" % (len(dead), ", ".join(dead)))

    def test_persistent_loggers(self):
        # Logger objects are persistent oraz retain their configuration, even
        #  jeżeli visible references are destroyed.
        self.root_logger.setLevel(logging.INFO)
        foo = logging.getLogger("foo")
        self._watch_for_survival(foo)
        foo.setLevel(logging.DEBUG)
        self.root_logger.debug(self.next_message())
        foo.debug(self.next_message())
        self.assert_log_lines([
            ('foo', 'DEBUG', '2'),
        ])
        usuń foo
        # foo has survived.
        self._assertPrawdasurvival()
        # foo has retained its settings.
        bar = logging.getLogger("foo")
        bar.debug(self.next_message())
        self.assert_log_lines([
            ('foo', 'DEBUG', '2'),
            ('foo', 'DEBUG', '3'),
        ])


klasa EncodingTest(BaseTest):
    def test_encoding_plain_file(self):
        # In Python 2.x, a plain file object jest treated jako having no encoding.
        log = logging.getLogger("test")
        fd, fn = tempfile.mkstemp(".log", "test_logging-1-")
        os.close(fd)
        # the non-ascii data we write to the log.
        data = "foo\x80"
        spróbuj:
            handler = logging.FileHandler(fn, encoding="utf-8")
            log.addHandler(handler)
            spróbuj:
                # write non-ascii data to the log.
                log.warning(data)
            w_końcu:
                log.removeHandler(handler)
                handler.close()
            # check we wrote exactly those bytes, ignoring trailing \n etc
            f = open(fn, encoding="utf-8")
            spróbuj:
                self.assertEqual(f.read().rstrip(), data)
            w_końcu:
                f.close()
        w_końcu:
            jeżeli os.path.isfile(fn):
                os.remove(fn)

    def test_encoding_cyrillic_unicode(self):
        log = logging.getLogger("test")
        #Get a message w Unicode: Do svidanya w Cyrillic (meaning goodbye)
        message = '\u0434\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f'
        #Ensure it's written w a Cyrillic encoding
        writer_class = codecs.getwriter('cp1251')
        writer_class.encoding = 'cp1251'
        stream = io.BytesIO()
        writer = writer_class(stream, 'strict')
        handler = logging.StreamHandler(writer)
        log.addHandler(handler)
        spróbuj:
            log.warning(message)
        w_końcu:
            log.removeHandler(handler)
            handler.close()
        # check we wrote exactly those bytes, ignoring trailing \n etc
        s = stream.getvalue()
        #Compare against what the data should be when encoded w CP-1251
        self.assertEqual(s, b'\xe4\xee \xf1\xe2\xe8\xe4\xe0\xed\xe8\xff\n')


klasa WarningsTest(BaseTest):

    def test_warnings(self):
        przy warnings.catch_warnings():
            logging.captureWarnings(Prawda)
            self.addCleanup(logging.captureWarnings, Nieprawda)
            warnings.filterwarnings("always", category=UserWarning)
            stream = io.StringIO()
            h = logging.StreamHandler(stream)
            logger = logging.getLogger("py.warnings")
            logger.addHandler(h)
            warnings.warn("I'm warning you...")
            logger.removeHandler(h)
            s = stream.getvalue()
            h.close()
            self.assertGreater(s.find("UserWarning: I'm warning you...\n"), 0)

            #See jeżeli an explicit file uses the original implementation
            a_file = io.StringIO()
            warnings.showwarning("Explicit", UserWarning, "dummy.py", 42,
                                 a_file, "Dummy line")
            s = a_file.getvalue()
            a_file.close()
            self.assertEqual(s,
                "dummy.py:42: UserWarning: Explicit\n  Dummy line\n")

    def test_warnings_no_handlers(self):
        przy warnings.catch_warnings():
            logging.captureWarnings(Prawda)
            self.addCleanup(logging.captureWarnings, Nieprawda)

            # confirm our assumption: no loggers are set
            logger = logging.getLogger("py.warnings")
            self.assertEqual(logger.handlers, [])

            warnings.showwarning("Explicit", UserWarning, "dummy.py", 42)
            self.assertEqual(len(logger.handlers), 1)
            self.assertIsInstance(logger.handlers[0], logging.NullHandler)


def formatFunc(format, datefmt=Nic):
    zwróć logging.Formatter(format, datefmt)

def handlerFunc():
    zwróć logging.StreamHandler()

klasa CustomHandler(logging.StreamHandler):
    dalej

klasa ConfigDictTest(BaseTest):

    """Reading logging config z a dictionary."""

    expected_log_pat = r"^(\w+) \+\+ (\w+)$"

    # config0 jest a standard configuration.
    config0 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'root' : {
            'level' : 'WARNING',
            'handlers' : ['hand1'],
        },
    }

    # config1 adds a little to the standard configuration.
    config1 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    # config1a moves the handler to the root. Used przy config8a
    config1a = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
            },
        },
        'root' : {
            'level' : 'WARNING',
            'handlers' : ['hand1'],
        },
    }

    # config2 has a subtle configuration error that should be reported
    config2 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdbout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    #As config1 but przy a misspelt level on a handler
    config2a = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NTOSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }


    #As config1 but przy a misspelt level on a logger
    config2b = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WRANING',
        },
    }

    # config3 has a less subtle configuration error
    config3 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'misspelled_name',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    # config4 specifies a custom formatter klasa to be loaded
    config4 = {
        'version': 1,
        'formatters': {
            'form1' : {
                '()' : __name__ + '.ExceptionFormatter',
                'format' : '%(levelname)s:%(name)s:%(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'root' : {
            'level' : 'NOTSET',
                'handlers' : ['hand1'],
        },
    }

    # As config4 but using an actual callable rather than a string
    config4a = {
        'version': 1,
        'formatters': {
            'form1' : {
                '()' : ExceptionFormatter,
                'format' : '%(levelname)s:%(name)s:%(message)s',
            },
            'form2' : {
                '()' : __name__ + '.formatFunc',
                'format' : '%(levelname)s:%(name)s:%(message)s',
            },
            'form3' : {
                '()' : formatFunc,
                'format' : '%(levelname)s:%(name)s:%(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
            'hand2' : {
                '()' : handlerFunc,
            },
        },
        'root' : {
            'level' : 'NOTSET',
                'handlers' : ['hand1'],
        },
    }

    # config5 specifies a custom handler klasa to be loaded
    config5 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : __name__ + '.CustomHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    # config6 specifies a custom handler klasa to be loaded
    # but has bad arguments
    config6 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : __name__ + '.CustomHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
                '9' : 'invalid parameter name',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    #config 7 does nie define compiler.parser but defines compiler.lexer
    #so compiler.parser should be disabled after applying it
    config7 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.lexer' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    # config8 defines both compiler oraz compiler.lexer
    # so compiler.parser should nie be disabled (since
    # compiler jest defined)
    config8 = {
        'version': 1,
        'disable_existing_loggers' : Nieprawda,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
            'compiler.lexer' : {
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    # config8a disables existing loggers
    config8a = {
        'version': 1,
        'disable_existing_loggers' : Prawda,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
            'compiler.lexer' : {
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    config9 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'WARNING',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'WARNING',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'NOTSET',
        },
    }

    config9a = {
        'version': 1,
        'incremental' : Prawda,
        'handlers' : {
            'hand1' : {
                'level' : 'WARNING',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'INFO',
            },
        },
    }

    config9b = {
        'version': 1,
        'incremental' : Prawda,
        'handlers' : {
            'hand1' : {
                'level' : 'INFO',
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'INFO',
            },
        },
    }

    #As config1 but przy a filter added
    config10 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'filters' : {
            'filt1' : {
                'name' : 'compiler.parser',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
                'filters' : ['filt1'],
            },
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'filters' : ['filt1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
            'handlers' : ['hand1'],
        },
    }

    #As config1 but using cfg:// references
    config11 = {
        'version': 1,
        'true_formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handler_configs': {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'formatters' : 'cfg://true_formatters',
        'handlers' : {
            'hand1' : 'cfg://handler_configs[hand1]',
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    #As config11 but missing the version key
    config12 = {
        'true_formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handler_configs': {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'formatters' : 'cfg://true_formatters',
        'handlers' : {
            'hand1' : 'cfg://handler_configs[hand1]',
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    #As config11 but using an unsupported version
    config13 = {
        'version': 2,
        'true_formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handler_configs': {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
            },
        },
        'formatters' : 'cfg://true_formatters',
        'handlers' : {
            'hand1' : 'cfg://handler_configs[hand1]',
        },
        'loggers' : {
            'compiler.parser' : {
                'level' : 'DEBUG',
                'handlers' : ['hand1'],
            },
        },
        'root' : {
            'level' : 'WARNING',
        },
    }

    # As config0, but przy properties
    config14 = {
        'version': 1,
        'formatters': {
            'form1' : {
                'format' : '%(levelname)s ++ %(message)s',
            },
        },
        'handlers' : {
            'hand1' : {
                'class' : 'logging.StreamHandler',
                'formatter' : 'form1',
                'level' : 'NOTSET',
                'stream'  : 'ext://sys.stdout',
                '.': {
                    'foo': 'bar',
                    'terminator': '!\n',
                }
            },
        },
        'root' : {
            'level' : 'WARNING',
            'handlers' : ['hand1'],
        },
    }

    out_of_order = {
        "version": 1,
        "formatters": {
            "mySimpleFormatter": {
                "format": "%(asctime)s (%(name)s) %(levelname)s: %(message)s",
                "style": "$"
            }
        },
        "handlers": {
            "fileGlobal": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "mySimpleFormatter"
            },
            "bufferGlobal": {
                "class": "logging.handlers.MemoryHandler",
                "capacity": 5,
                "formatter": "mySimpleFormatter",
                "target": "fileGlobal",
                "level": "DEBUG"
                }
        },
        "loggers": {
            "mymodule": {
                "level": "DEBUG",
                "handlers": ["bufferGlobal"],
                "propagate": "true"
            }
        }
    }

    def apply_config(self, conf):
        logging.config.dictConfig(conf)

    def test_config0_ok(self):
        # A simple config which overrides the default settings.
        przy support.captured_stdout() jako output:
            self.apply_config(self.config0)
            logger = logging.getLogger()
            # Won't output anything
            logger.info(self.next_message())
            # Outputs a message
            logger.error(self.next_message())
            self.assert_log_lines([
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config1_ok(self, config=config1):
        # A config defining a sub-parser jako well.
        przy support.captured_stdout() jako output:
            self.apply_config(config)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config2_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(Exception, self.apply_config, self.config2)

    def test_config2a_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(Exception, self.apply_config, self.config2a)

    def test_config2b_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(Exception, self.apply_config, self.config2b)

    def test_config3_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(Exception, self.apply_config, self.config3)

    def test_config4_ok(self):
        # A config specifying a custom formatter class.
        przy support.captured_stdout() jako output:
            self.apply_config(self.config4)
            #logger = logging.getLogger()
            spróbuj:
                podnieś RuntimeError()
            wyjąwszy RuntimeError:
                logging.exception("just testing")
            sys.stdout.seek(0)
            self.assertEqual(output.getvalue(),
                "ERROR:root:just testing\nGot a [RuntimeError]\n")
            # Original logger output jest empty
            self.assert_log_lines([])

    def test_config4a_ok(self):
        # A config specifying a custom formatter class.
        przy support.captured_stdout() jako output:
            self.apply_config(self.config4a)
            #logger = logging.getLogger()
            spróbuj:
                podnieś RuntimeError()
            wyjąwszy RuntimeError:
                logging.exception("just testing")
            sys.stdout.seek(0)
            self.assertEqual(output.getvalue(),
                "ERROR:root:just testing\nGot a [RuntimeError]\n")
            # Original logger output jest empty
            self.assert_log_lines([])

    def test_config5_ok(self):
        self.test_config1_ok(config=self.config5)

    def test_config6_failure(self):
        self.assertRaises(Exception, self.apply_config, self.config6)

    def test_config7_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config1)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])
        przy support.captured_stdout() jako output:
            self.apply_config(self.config7)
            logger = logging.getLogger("compiler.parser")
            self.assertPrawda(logger.disabled)
            logger = logging.getLogger("compiler.lexer")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '3'),
                ('ERROR', '4'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    #Same jako test_config_7_ok but don't disable old loggers.
    def test_config_8_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config1)
            logger = logging.getLogger("compiler.parser")
            # All will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])
        przy support.captured_stdout() jako output:
            self.apply_config(self.config8)
            logger = logging.getLogger("compiler.parser")
            self.assertNieprawda(logger.disabled)
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            logger = logging.getLogger("compiler.lexer")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '3'),
                ('ERROR', '4'),
                ('INFO', '5'),
                ('ERROR', '6'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config_8a_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config1a)
            logger = logging.getLogger("compiler.parser")
            # See issue #11424. compiler-hyphenated sorts
            # between compiler oraz compiler.xyz oraz this
            # was preventing compiler.xyz z being included
            # w the child loggers of compiler because of an
            # overzealous loop termination condition.
            hyphenated = logging.getLogger('compiler-hyphenated')
            # All will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            hyphenated.critical(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
                ('CRITICAL', '3'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])
        przy support.captured_stdout() jako output:
            self.apply_config(self.config8a)
            logger = logging.getLogger("compiler.parser")
            self.assertNieprawda(logger.disabled)
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            logger = logging.getLogger("compiler.lexer")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            # Will nie appear
            hyphenated.critical(self.next_message())
            self.assert_log_lines([
                ('INFO', '4'),
                ('ERROR', '5'),
                ('INFO', '6'),
                ('ERROR', '7'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    def test_config_9_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config9)
            logger = logging.getLogger("compiler.parser")
            #Nothing will be output since both handler oraz logger are set to WARNING
            logger.info(self.next_message())
            self.assert_log_lines([], stream=output)
            self.apply_config(self.config9a)
            #Nothing will be output since both handler jest still set to WARNING
            logger.info(self.next_message())
            self.assert_log_lines([], stream=output)
            self.apply_config(self.config9b)
            #Message should now be output
            logger.info(self.next_message())
            self.assert_log_lines([
                ('INFO', '3'),
            ], stream=output)

    def test_config_10_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config10)
            logger = logging.getLogger("compiler.parser")
            logger.warning(self.next_message())
            logger = logging.getLogger('compiler')
            #Not output, because filtered
            logger.warning(self.next_message())
            logger = logging.getLogger('compiler.lexer')
            #Not output, because filtered
            logger.warning(self.next_message())
            logger = logging.getLogger("compiler.parser.codegen")
            #Output, jako nie filtered
            logger.error(self.next_message())
            self.assert_log_lines([
                ('WARNING', '1'),
                ('ERROR', '4'),
            ], stream=output)

    def test_config11_ok(self):
        self.test_config1_ok(self.config11)

    def test_config12_failure(self):
        self.assertRaises(Exception, self.apply_config, self.config12)

    def test_config13_failure(self):
        self.assertRaises(Exception, self.apply_config, self.config13)

    def test_config14_ok(self):
        przy support.captured_stdout() jako output:
            self.apply_config(self.config14)
            h = logging._handlers['hand1']
            self.assertEqual(h.foo, 'bar')
            self.assertEqual(h.terminator, '!\n')
            logging.warning('Exclamation')
            self.assertPrawda(output.getvalue().endswith('Exclamation!\n'))

    @unittest.skipUnless(threading, 'listen() needs threading to work')
    def setup_via_listener(self, text, verify=Nic):
        text = text.encode("utf-8")
        # Ask dla a randomly assigned port (by using port 0)
        t = logging.config.listen(0, verify)
        t.start()
        t.ready.wait()
        # Now get the port allocated
        port = t.port
        t.ready.clear()
        spróbuj:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect(('localhost', port))

            slen = struct.pack('>L', len(text))
            s = slen + text
            sentsofar = 0
            left = len(s)
            dopóki left > 0:
                sent = sock.send(s[sentsofar:])
                sentsofar += sent
                left -= sent
            sock.close()
        w_końcu:
            t.ready.wait(2.0)
            logging.config.stopListening()
            t.join(2.0)

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_listen_config_10_ok(self):
        przy support.captured_stdout() jako output:
            self.setup_via_listener(json.dumps(self.config10))
            logger = logging.getLogger("compiler.parser")
            logger.warning(self.next_message())
            logger = logging.getLogger('compiler')
            #Not output, because filtered
            logger.warning(self.next_message())
            logger = logging.getLogger('compiler.lexer')
            #Not output, because filtered
            logger.warning(self.next_message())
            logger = logging.getLogger("compiler.parser.codegen")
            #Output, jako nie filtered
            logger.error(self.next_message())
            self.assert_log_lines([
                ('WARNING', '1'),
                ('ERROR', '4'),
            ], stream=output)

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_listen_config_1_ok(self):
        przy support.captured_stdout() jako output:
            self.setup_via_listener(textwrap.dedent(ConfigFileTest.config1))
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output jest empty.
            self.assert_log_lines([])

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_listen_verify(self):

        def verify_fail(stuff):
            zwróć Nic

        def verify_reverse(stuff):
            zwróć stuff[::-1]

        logger = logging.getLogger("compiler.parser")
        to_send = textwrap.dedent(ConfigFileTest.config1)
        # First, specify a verification function that will fail.
        # We expect to see no output, since our configuration
        # never took effect.
        przy support.captured_stdout() jako output:
            self.setup_via_listener(to_send, verify_fail)
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
        self.assert_log_lines([], stream=output)
        # Original logger output has the stuff we logged.
        self.assert_log_lines([
            ('INFO', '1'),
            ('ERROR', '2'),
        ], pat=r"^[\w.]+ -> (\w+): (\d+)$")

        # Now, perform no verification. Our configuration
        # should take effect.

        przy support.captured_stdout() jako output:
            self.setup_via_listener(to_send)    # no verify callable specified
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
        self.assert_log_lines([
            ('INFO', '3'),
            ('ERROR', '4'),
        ], stream=output)
        # Original logger output still has the stuff we logged before.
        self.assert_log_lines([
            ('INFO', '1'),
            ('ERROR', '2'),
        ], pat=r"^[\w.]+ -> (\w+): (\d+)$")

        # Now, perform verification which transforms the bytes.

        przy support.captured_stdout() jako output:
            self.setup_via_listener(to_send[::-1], verify_reverse)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
        self.assert_log_lines([
            ('INFO', '5'),
            ('ERROR', '6'),
        ], stream=output)
        # Original logger output still has the stuff we logged before.
        self.assert_log_lines([
            ('INFO', '1'),
            ('ERROR', '2'),
        ], pat=r"^[\w.]+ -> (\w+): (\d+)$")

    def test_out_of_order(self):
        self.apply_config(self.out_of_order)
        handler = logging.getLogger('mymodule').handlers[0]
        self.assertIsInstance(handler.target, logging.Handler)
        self.assertIsInstance(handler.formatter._style,
                              logging.StringTemplateStyle)

    def test_baseconfig(self):
        d = {
            'atuple': (1, 2, 3),
            'alist': ['a', 'b', 'c'],
            'adict': {'d': 'e', 'f': 3 },
            'nest1': ('g', ('h', 'i'), 'j'),
            'nest2': ['k', ['l', 'm'], 'n'],
            'nest3': ['o', 'cfg://alist', 'p'],
        }
        bc = logging.config.BaseConfigurator(d)
        self.assertEqual(bc.convert('cfg://atuple[1]'), 2)
        self.assertEqual(bc.convert('cfg://alist[1]'), 'b')
        self.assertEqual(bc.convert('cfg://nest1[1][0]'), 'h')
        self.assertEqual(bc.convert('cfg://nest2[1][1]'), 'm')
        self.assertEqual(bc.convert('cfg://adict.d'), 'e')
        self.assertEqual(bc.convert('cfg://adict[f]'), 3)
        v = bc.convert('cfg://nest3')
        self.assertEqual(v.pop(1), ['a', 'b', 'c'])
        self.assertRaises(KeyError, bc.convert, 'cfg://nosuch')
        self.assertRaises(ValueError, bc.convert, 'cfg://!')
        self.assertRaises(KeyError, bc.convert, 'cfg://adict[2]')

klasa ManagerTest(BaseTest):
    def test_manager_loggerclass(self):
        logged = []

        klasa MyLogger(logging.Logger):
            def _log(self, level, msg, args, exc_info=Nic, extra=Nic):
                logged.append(msg)

        man = logging.Manager(Nic)
        self.assertRaises(TypeError, man.setLoggerClass, int)
        man.setLoggerClass(MyLogger)
        logger = man.getLogger('test')
        logger.warning('should appear w logged')
        logging.warning('should nie appear w logged')

        self.assertEqual(logged, ['should appear w logged'])

    def test_set_log_record_factory(self):
        man = logging.Manager(Nic)
        expected = object()
        man.setLogRecordFactory(expected)
        self.assertEqual(man.logRecordFactory, expected)

klasa ChildLoggerTest(BaseTest):
    def test_child_loggers(self):
        r = logging.getLogger()
        l1 = logging.getLogger('abc')
        l2 = logging.getLogger('def.ghi')
        c1 = r.getChild('xyz')
        c2 = r.getChild('uvw.xyz')
        self.assertIs(c1, logging.getLogger('xyz'))
        self.assertIs(c2, logging.getLogger('uvw.xyz'))
        c1 = l1.getChild('def')
        c2 = c1.getChild('ghi')
        c3 = l1.getChild('def.ghi')
        self.assertIs(c1, logging.getLogger('abc.def'))
        self.assertIs(c2, logging.getLogger('abc.def.ghi'))
        self.assertIs(c2, c3)


klasa DerivedLogRecord(logging.LogRecord):
    dalej

klasa LogRecordFactoryTest(BaseTest):

    def setUp(self):
        klasa CheckingFilter(logging.Filter):
            def __init__(self, cls):
                self.cls = cls

            def filter(self, record):
                t = type(record)
                jeżeli t jest nie self.cls:
                    msg = 'Unexpected LogRecord type %s, expected %s' % (t,
                            self.cls)
                    podnieś TypeError(msg)
                zwróć Prawda

        BaseTest.setUp(self)
        self.filter = CheckingFilter(DerivedLogRecord)
        self.root_logger.addFilter(self.filter)
        self.orig_factory = logging.getLogRecordFactory()

    def tearDown(self):
        self.root_logger.removeFilter(self.filter)
        BaseTest.tearDown(self)
        logging.setLogRecordFactory(self.orig_factory)

    def test_logrecord_class(self):
        self.assertRaises(TypeError, self.root_logger.warning,
                          self.next_message())
        logging.setLogRecordFactory(DerivedLogRecord)
        self.root_logger.error(self.next_message())
        self.assert_log_lines([
           ('root', 'ERROR', '2'),
        ])


klasa QueueHandlerTest(BaseTest):
    # Do nie bother przy a logger name group.
    expected_log_pat = r"^[\w.]+ -> (\w+): (\d+)$"

    def setUp(self):
        BaseTest.setUp(self)
        self.queue = queue.Queue(-1)
        self.que_hdlr = logging.handlers.QueueHandler(self.queue)
        self.que_logger = logging.getLogger('que')
        self.que_logger.propagate = Nieprawda
        self.que_logger.setLevel(logging.WARNING)
        self.que_logger.addHandler(self.que_hdlr)

    def tearDown(self):
        self.que_hdlr.close()
        BaseTest.tearDown(self)

    def test_queue_handler(self):
        self.que_logger.debug(self.next_message())
        self.assertRaises(queue.Empty, self.queue.get_nowait)
        self.que_logger.info(self.next_message())
        self.assertRaises(queue.Empty, self.queue.get_nowait)
        msg = self.next_message()
        self.que_logger.warning(msg)
        data = self.queue.get_nowait()
        self.assertPrawda(isinstance(data, logging.LogRecord))
        self.assertEqual(data.name, self.que_logger.name)
        self.assertEqual((data.msg, data.args), (msg, Nic))

    @unittest.skipUnless(hasattr(logging.handlers, 'QueueListener'),
                         'logging.handlers.QueueListener required dla this test')
    def test_queue_listener(self):
        handler = support.TestHandler(support.Matcher())
        listener = logging.handlers.QueueListener(self.queue, handler)
        listener.start()
        spróbuj:
            self.que_logger.warning(self.next_message())
            self.que_logger.error(self.next_message())
            self.que_logger.critical(self.next_message())
        w_końcu:
            listener.stop()
        self.assertPrawda(handler.matches(levelno=logging.WARNING, message='1'))
        self.assertPrawda(handler.matches(levelno=logging.ERROR, message='2'))
        self.assertPrawda(handler.matches(levelno=logging.CRITICAL, message='3'))
        handler.close()

        # Now test przy respect_handler_level set

        handler = support.TestHandler(support.Matcher())
        handler.setLevel(logging.CRITICAL)
        listener = logging.handlers.QueueListener(self.queue, handler,
                                                  respect_handler_level=Prawda)
        listener.start()
        spróbuj:
            self.que_logger.warning(self.next_message())
            self.que_logger.error(self.next_message())
            self.que_logger.critical(self.next_message())
        w_końcu:
            listener.stop()
        self.assertNieprawda(handler.matches(levelno=logging.WARNING, message='4'))
        self.assertNieprawda(handler.matches(levelno=logging.ERROR, message='5'))
        self.assertPrawda(handler.matches(levelno=logging.CRITICAL, message='6'))


ZERO = datetime.timedelta(0)

klasa UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        zwróć ZERO

    dst = utcoffset

    def tzname(self, dt):
        zwróć 'UTC'

utc = UTC()

klasa FormatterTest(unittest.TestCase):
    def setUp(self):
        self.common = {
            'name': 'formatter.test',
            'level': logging.DEBUG,
            'pathname': os.path.join('path', 'to', 'dummy.ext'),
            'lineno': 42,
            'exc_info': Nic,
            'func': Nic,
            'msg': 'Message przy %d %s',
            'args': (2, 'placeholders'),
        }
        self.variants = {
        }

    def get_record(self, name=Nic):
        result = dict(self.common)
        jeżeli name jest nie Nic:
            result.update(self.variants[name])
        zwróć logging.makeLogRecord(result)

    def test_percent(self):
        # Test %-formatting
        r = self.get_record()
        f = logging.Formatter('${%(message)s}')
        self.assertEqual(f.format(r), '${Message przy 2 placeholders}')
        f = logging.Formatter('%(random)s')
        self.assertRaises(KeyError, f.format, r)
        self.assertNieprawda(f.usesTime())
        f = logging.Formatter('%(asctime)s')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('%(asctime)-15s')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('asctime')
        self.assertNieprawda(f.usesTime())

    def test_braces(self):
        # Test {}-formatting
        r = self.get_record()
        f = logging.Formatter('$%{message}%$', style='{')
        self.assertEqual(f.format(r), '$%Message przy 2 placeholders%$')
        f = logging.Formatter('{random}', style='{')
        self.assertRaises(KeyError, f.format, r)
        self.assertNieprawda(f.usesTime())
        f = logging.Formatter('{asctime}', style='{')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('{asctime!s:15}', style='{')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('{asctime:15}', style='{')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('asctime', style='{')
        self.assertNieprawda(f.usesTime())

    def test_dollars(self):
        # Test $-formatting
        r = self.get_record()
        f = logging.Formatter('$message', style='$')
        self.assertEqual(f.format(r), 'Message przy 2 placeholders')
        f = logging.Formatter('$$%${message}%$$', style='$')
        self.assertEqual(f.format(r), '$%Message przy 2 placeholders%$')
        f = logging.Formatter('${random}', style='$')
        self.assertRaises(KeyError, f.format, r)
        self.assertNieprawda(f.usesTime())
        f = logging.Formatter('${asctime}', style='$')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('${asctime', style='$')
        self.assertNieprawda(f.usesTime())
        f = logging.Formatter('$asctime', style='$')
        self.assertPrawda(f.usesTime())
        f = logging.Formatter('asctime', style='$')
        self.assertNieprawda(f.usesTime())

    def test_invalid_style(self):
        self.assertRaises(ValueError, logging.Formatter, Nic, Nic, 'x')

    def test_time(self):
        r = self.get_record()
        dt = datetime.datetime(1993, 4, 21, 8, 3, 0, 0, utc)
        # We use Nic to indicate we want the local timezone
        # We're essentially converting a UTC time to local time
        r.created = time.mktime(dt.astimezone(Nic).timetuple())
        r.msecs = 123
        f = logging.Formatter('%(asctime)s %(message)s')
        f.converter = time.gmtime
        self.assertEqual(f.formatTime(r), '1993-04-21 08:03:00,123')
        self.assertEqual(f.formatTime(r, '%Y:%d'), '1993:21')
        f.format(r)
        self.assertEqual(r.asctime, '1993-04-21 08:03:00,123')

klasa TestBufferingFormatter(logging.BufferingFormatter):
    def formatHeader(self, records):
        zwróć '[(%d)' % len(records)

    def formatFooter(self, records):
        zwróć '(%d)]' % len(records)

klasa BufferingFormatterTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            logging.makeLogRecord({'msg': 'one'}),
            logging.makeLogRecord({'msg': 'two'}),
        ]

    def test_default(self):
        f = logging.BufferingFormatter()
        self.assertEqual('', f.format([]))
        self.assertEqual('onetwo', f.format(self.records))

    def test_custom(self):
        f = TestBufferingFormatter()
        self.assertEqual('[(2)onetwo(2)]', f.format(self.records))
        lf = logging.Formatter('<%(message)s>')
        f = TestBufferingFormatter(lf)
        self.assertEqual('[(2)<one><two>(2)]', f.format(self.records))

klasa ExceptionTest(BaseTest):
    def test_formatting(self):
        r = self.root_logger
        h = RecordingHandler()
        r.addHandler(h)
        spróbuj:
            podnieś RuntimeError('deliberate mistake')
        wyjąwszy:
            logging.exception('failed', stack_info=Prawda)
        r.removeHandler(h)
        h.close()
        r = h.records[0]
        self.assertPrawda(r.exc_text.startswith('Traceback (most recent '
                                              'call last):\n'))
        self.assertPrawda(r.exc_text.endswith('\nRuntimeError: '
                                            'deliberate mistake'))
        self.assertPrawda(r.stack_info.startswith('Stack (most recent '
                                              'call last):\n'))
        self.assertPrawda(r.stack_info.endswith('logging.exception(\'failed\', '
                                            'stack_info=Prawda)'))


klasa LastResortTest(BaseTest):
    def test_last_resort(self):
        # Test the last resort handler
        root = self.root_logger
        root.removeHandler(self.root_hdlr)
        old_lastresort = logging.lastResort
        old_raise_exceptions = logging.raiseExceptions

        spróbuj:
            przy support.captured_stderr() jako stderr:
                root.debug('This should nie appear')
                self.assertEqual(stderr.getvalue(), '')
                root.warning('Final chance!')
                self.assertEqual(stderr.getvalue(), 'Final chance!\n')

            # No handlers oraz no last resort, so 'No handlers' message
            logging.lastResort = Nic
            przy support.captured_stderr() jako stderr:
                root.warning('Final chance!')
                msg = 'No handlers could be found dla logger "root"\n'
                self.assertEqual(stderr.getvalue(), msg)

            # 'No handlers' message only printed once
            przy support.captured_stderr() jako stderr:
                root.warning('Final chance!')
                self.assertEqual(stderr.getvalue(), '')

            # If podnieśExceptions jest Nieprawda, no message jest printed
            root.manager.emittedNoHandlerWarning = Nieprawda
            logging.raiseExceptions = Nieprawda
            przy support.captured_stderr() jako stderr:
                root.warning('Final chance!')
                self.assertEqual(stderr.getvalue(), '')
        w_końcu:
            root.addHandler(self.root_hdlr)
            logging.lastResort = old_lastresort
            logging.raiseExceptions = old_raise_exceptions


klasa FakeHandler:

    def __init__(self, identifier, called):
        dla method w ('acquire', 'flush', 'close', 'release'):
            setattr(self, method, self.record_call(identifier, method, called))

    def record_call(self, identifier, method_name, called):
        def inner():
            called.append('{} - {}'.format(identifier, method_name))
        zwróć inner


klasa RecordingHandler(logging.NullHandler):

    def __init__(self, *args, **kwargs):
        super(RecordingHandler, self).__init__(*args, **kwargs)
        self.records = []

    def handle(self, record):
        """Keep track of all the emitted records."""
        self.records.append(record)


klasa ShutdownTest(BaseTest):

    """Test suite dla the shutdown method."""

    def setUp(self):
        super(ShutdownTest, self).setUp()
        self.called = []

        podnieś_exceptions = logging.raiseExceptions
        self.addCleanup(setattr, logging, 'raiseExceptions', podnieś_exceptions)

    def podnieś_error(self, error):
        def inner():
            podnieś error()
        zwróć inner

    def test_no_failure(self):
        # create some fake handlers
        handler0 = FakeHandler(0, self.called)
        handler1 = FakeHandler(1, self.called)
        handler2 = FakeHandler(2, self.called)

        # create live weakref to those handlers
        handlers = map(logging.weakref.ref, [handler0, handler1, handler2])

        logging.shutdown(handlerList=list(handlers))

        expected = ['2 - acquire', '2 - flush', '2 - close', '2 - release',
                    '1 - acquire', '1 - flush', '1 - close', '1 - release',
                    '0 - acquire', '0 - flush', '0 - close', '0 - release']
        self.assertEqual(expected, self.called)

    def _test_with_failure_in_method(self, method, error):
        handler = FakeHandler(0, self.called)
        setattr(handler, method, self.raise_error(error))
        handlers = [logging.weakref.ref(handler)]

        logging.shutdown(handlerList=list(handlers))

        self.assertEqual('0 - release', self.called[-1])

    def test_with_ioerror_in_acquire(self):
        self._test_with_failure_in_method('acquire', OSError)

    def test_with_ioerror_in_flush(self):
        self._test_with_failure_in_method('flush', OSError)

    def test_with_ioerror_in_close(self):
        self._test_with_failure_in_method('close', OSError)

    def test_with_valueerror_in_acquire(self):
        self._test_with_failure_in_method('acquire', ValueError)

    def test_with_valueerror_in_flush(self):
        self._test_with_failure_in_method('flush', ValueError)

    def test_with_valueerror_in_close(self):
        self._test_with_failure_in_method('close', ValueError)

    def test_with_other_error_in_acquire_without_raise(self):
        logging.raiseExceptions = Nieprawda
        self._test_with_failure_in_method('acquire', IndexError)

    def test_with_other_error_in_flush_without_raise(self):
        logging.raiseExceptions = Nieprawda
        self._test_with_failure_in_method('flush', IndexError)

    def test_with_other_error_in_close_without_raise(self):
        logging.raiseExceptions = Nieprawda
        self._test_with_failure_in_method('close', IndexError)

    def test_with_other_error_in_acquire_with_raise(self):
        logging.raiseExceptions = Prawda
        self.assertRaises(IndexError, self._test_with_failure_in_method,
                          'acquire', IndexError)

    def test_with_other_error_in_flush_with_raise(self):
        logging.raiseExceptions = Prawda
        self.assertRaises(IndexError, self._test_with_failure_in_method,
                          'flush', IndexError)

    def test_with_other_error_in_close_with_raise(self):
        logging.raiseExceptions = Prawda
        self.assertRaises(IndexError, self._test_with_failure_in_method,
                          'close', IndexError)


klasa ModuleLevelMiscTest(BaseTest):

    """Test suite dla some module level methods."""

    def test_disable(self):
        old_disable = logging.root.manager.disable
        # confirm our assumptions are correct
        self.assertEqual(old_disable, 0)
        self.addCleanup(logging.disable, old_disable)

        logging.disable(83)
        self.assertEqual(logging.root.manager.disable, 83)

    def _test_log(self, method, level=Nic):
        called = []
        support.patch(self, logging, 'basicConfig',
                      lambda *a, **kw: called.append((a, kw)))

        recording = RecordingHandler()
        logging.root.addHandler(recording)

        log_method = getattr(logging, method)
        jeżeli level jest nie Nic:
            log_method(level, "test me: %r", recording)
        inaczej:
            log_method("test me: %r", recording)

        self.assertEqual(len(recording.records), 1)
        record = recording.records[0]
        self.assertEqual(record.getMessage(), "test me: %r" % recording)

        expected_level = level jeżeli level jest nie Nic inaczej getattr(logging, method.upper())
        self.assertEqual(record.levelno, expected_level)

        # basicConfig was nie called!
        self.assertEqual(called, [])

    def test_log(self):
        self._test_log('log', logging.ERROR)

    def test_debug(self):
        self._test_log('debug')

    def test_info(self):
        self._test_log('info')

    def test_warning(self):
        self._test_log('warning')

    def test_error(self):
        self._test_log('error')

    def test_critical(self):
        self._test_log('critical')

    def test_set_logger_class(self):
        self.assertRaises(TypeError, logging.setLoggerClass, object)

        klasa MyLogger(logging.Logger):
            dalej

        logging.setLoggerClass(MyLogger)
        self.assertEqual(logging.getLoggerClass(), MyLogger)

        logging.setLoggerClass(logging.Logger)
        self.assertEqual(logging.getLoggerClass(), logging.Logger)

    def test_logging_at_shutdown(self):
        # Issue #20037
        code = """jeżeli 1:
            zaimportuj logging

            klasa A:
                def __del__(self):
                    spróbuj:
                        podnieś ValueError("some error")
                    wyjąwszy Exception:
                        logging.exception("exception w __del__")

            a = A()"""
        rc, out, err = assert_python_ok("-c", code)
        err = err.decode()
        self.assertIn("exception w __del__", err)
        self.assertIn("ValueError: some error", err)


klasa LogRecordTest(BaseTest):
    def test_str_rep(self):
        r = logging.makeLogRecord({})
        s = str(r)
        self.assertPrawda(s.startswith('<LogRecord: '))
        self.assertPrawda(s.endswith('>'))

    def test_dict_arg(self):
        h = RecordingHandler()
        r = logging.getLogger()
        r.addHandler(h)
        d = {'less' : 'more' }
        logging.warning('less jest %(less)s', d)
        self.assertIs(h.records[0].args, d)
        self.assertEqual(h.records[0].message, 'less jest more')
        r.removeHandler(h)
        h.close()

    def test_multiprocessing(self):
        r = logging.makeLogRecord({})
        self.assertEqual(r.processName, 'MainProcess')
        spróbuj:
            zaimportuj multiprocessing jako mp
            r = logging.makeLogRecord({})
            self.assertEqual(r.processName, mp.current_process().name)
        wyjąwszy ImportError:
            dalej

    def test_optional(self):
        r = logging.makeLogRecord({})
        NOT_NONE = self.assertIsNotNic
        jeżeli threading:
            NOT_NONE(r.thread)
            NOT_NONE(r.threadName)
        NOT_NONE(r.process)
        NOT_NONE(r.processName)
        log_threads = logging.logThreads
        log_processes = logging.logProcesses
        log_multiprocessing = logging.logMultiprocessing
        spróbuj:
            logging.logThreads = Nieprawda
            logging.logProcesses = Nieprawda
            logging.logMultiprocessing = Nieprawda
            r = logging.makeLogRecord({})
            NONE = self.assertIsNic
            NONE(r.thread)
            NONE(r.threadName)
            NONE(r.process)
            NONE(r.processName)
        w_końcu:
            logging.logThreads = log_threads
            logging.logProcesses = log_processes
            logging.logMultiprocessing = log_multiprocessing

klasa BasicConfigTest(unittest.TestCase):

    """Test suite dla logging.basicConfig."""

    def setUp(self):
        super(BasicConfigTest, self).setUp()
        self.handlers = logging.root.handlers
        self.saved_handlers = logging._handlers.copy()
        self.saved_handler_list = logging._handlerList[:]
        self.original_logging_level = logging.root.level
        self.addCleanup(self.cleanup)
        logging.root.handlers = []

    def tearDown(self):
        dla h w logging.root.handlers[:]:
            logging.root.removeHandler(h)
            h.close()
        super(BasicConfigTest, self).tearDown()

    def cleanup(self):
        setattr(logging.root, 'handlers', self.handlers)
        logging._handlers.clear()
        logging._handlers.update(self.saved_handlers)
        logging._handlerList[:] = self.saved_handler_list
        logging.root.level = self.original_logging_level

    def test_no_kwargs(self):
        logging.basicConfig()

        # handler defaults to a StreamHandler to sys.stderr
        self.assertEqual(len(logging.root.handlers), 1)
        handler = logging.root.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.stream, sys.stderr)

        formatter = handler.formatter
        # format defaults to logging.BASIC_FORMAT
        self.assertEqual(formatter._style._fmt, logging.BASIC_FORMAT)
        # datefmt defaults to Nic
        self.assertIsNic(formatter.datefmt)
        # style defaults to %
        self.assertIsInstance(formatter._style, logging.PercentStyle)

        # level jest nie explicitly set
        self.assertEqual(logging.root.level, self.original_logging_level)

    def test_strformatstyle(self):
        przy support.captured_stdout() jako output:
            logging.basicConfig(stream=sys.stdout, style="{")
            logging.error("Log an error")
            sys.stdout.seek(0)
            self.assertEqual(output.getvalue().strip(),
                "ERROR:root:Log an error")

    def test_stringtemplatestyle(self):
        przy support.captured_stdout() jako output:
            logging.basicConfig(stream=sys.stdout, style="$")
            logging.error("Log an error")
            sys.stdout.seek(0)
            self.assertEqual(output.getvalue().strip(),
                "ERROR:root:Log an error")

    def test_filename(self):

        def cleanup(h1, h2, fn):
            h1.close()
            h2.close()
            os.remove(fn)

        logging.basicConfig(filename='test.log')

        self.assertEqual(len(logging.root.handlers), 1)
        handler = logging.root.handlers[0]
        self.assertIsInstance(handler, logging.FileHandler)

        expected = logging.FileHandler('test.log', 'a')
        self.assertEqual(handler.stream.mode, expected.stream.mode)
        self.assertEqual(handler.stream.name, expected.stream.name)
        self.addCleanup(cleanup, handler, expected, 'test.log')

    def test_filemode(self):

        def cleanup(h1, h2, fn):
            h1.close()
            h2.close()
            os.remove(fn)

        logging.basicConfig(filename='test.log', filemode='wb')

        handler = logging.root.handlers[0]
        expected = logging.FileHandler('test.log', 'wb')
        self.assertEqual(handler.stream.mode, expected.stream.mode)
        self.addCleanup(cleanup, handler, expected, 'test.log')

    def test_stream(self):
        stream = io.StringIO()
        self.addCleanup(stream.close)
        logging.basicConfig(stream=stream)

        self.assertEqual(len(logging.root.handlers), 1)
        handler = logging.root.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.stream, stream)

    def test_format(self):
        logging.basicConfig(format='foo')

        formatter = logging.root.handlers[0].formatter
        self.assertEqual(formatter._style._fmt, 'foo')

    def test_datefmt(self):
        logging.basicConfig(datefmt='bar')

        formatter = logging.root.handlers[0].formatter
        self.assertEqual(formatter.datefmt, 'bar')

    def test_style(self):
        logging.basicConfig(style='$')

        formatter = logging.root.handlers[0].formatter
        self.assertIsInstance(formatter._style, logging.StringTemplateStyle)

    def test_level(self):
        old_level = logging.root.level
        self.addCleanup(logging.root.setLevel, old_level)

        logging.basicConfig(level=57)
        self.assertEqual(logging.root.level, 57)
        # Test that second call has no effect
        logging.basicConfig(level=58)
        self.assertEqual(logging.root.level, 57)

    def test_incompatible(self):
        assertRaises = self.assertRaises
        handlers = [logging.StreamHandler()]
        stream = sys.stderr
        assertRaises(ValueError, logging.basicConfig, filename='test.log',
                                                     stream=stream)
        assertRaises(ValueError, logging.basicConfig, filename='test.log',
                                                     handlers=handlers)
        assertRaises(ValueError, logging.basicConfig, stream=stream,
                                                     handlers=handlers)
        # Issue 23207: test dla invalid kwargs
        assertRaises(ValueError, logging.basicConfig, loglevel=logging.INFO)
        # Should pop both filename oraz filemode even jeżeli filename jest Nic
        logging.basicConfig(filename=Nic, filemode='a')

    def test_handlers(self):
        handlers = [
            logging.StreamHandler(),
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(),
        ]
        f = logging.Formatter()
        handlers[2].setFormatter(f)
        logging.basicConfig(handlers=handlers)
        self.assertIs(handlers[0], logging.root.handlers[0])
        self.assertIs(handlers[1], logging.root.handlers[1])
        self.assertIs(handlers[2], logging.root.handlers[2])
        self.assertIsNotNic(handlers[0].formatter)
        self.assertIsNotNic(handlers[1].formatter)
        self.assertIs(handlers[2].formatter, f)
        self.assertIs(handlers[0].formatter, handlers[1].formatter)

    def _test_log(self, method, level=Nic):
        # logging.root has no handlers so basicConfig should be called
        called = []

        old_basic_config = logging.basicConfig
        def my_basic_config(*a, **kw):
            old_basic_config()
            old_level = logging.root.level
            logging.root.setLevel(100)  # avoid having messages w stderr
            self.addCleanup(logging.root.setLevel, old_level)
            called.append((a, kw))

        support.patch(self, logging, 'basicConfig', my_basic_config)

        log_method = getattr(logging, method)
        jeżeli level jest nie Nic:
            log_method(level, "test me")
        inaczej:
            log_method("test me")

        # basicConfig was called przy no arguments
        self.assertEqual(called, [((), {})])

    def test_log(self):
        self._test_log('log', logging.WARNING)

    def test_debug(self):
        self._test_log('debug')

    def test_info(self):
        self._test_log('info')

    def test_warning(self):
        self._test_log('warning')

    def test_error(self):
        self._test_log('error')

    def test_critical(self):
        self._test_log('critical')


klasa LoggerAdapterTest(unittest.TestCase):

    def setUp(self):
        super(LoggerAdapterTest, self).setUp()
        old_handler_list = logging._handlerList[:]

        self.recording = RecordingHandler()
        self.logger = logging.root
        self.logger.addHandler(self.recording)
        self.addCleanup(self.logger.removeHandler, self.recording)
        self.addCleanup(self.recording.close)

        def cleanup():
            logging._handlerList[:] = old_handler_list

        self.addCleanup(cleanup)
        self.addCleanup(logging.shutdown)
        self.adapter = logging.LoggerAdapter(logger=self.logger, extra=Nic)

    def test_exception(self):
        msg = 'testing exception: %r'
        exc = Nic
        spróbuj:
            1 / 0
        wyjąwszy ZeroDivisionError jako e:
            exc = e
            self.adapter.exception(msg, self.recording)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.levelno, logging.ERROR)
        self.assertEqual(record.msg, msg)
        self.assertEqual(record.args, (self.recording,))
        self.assertEqual(record.exc_info,
                         (exc.__class__, exc, exc.__traceback__))

    def test_exception_excinfo(self):
        spróbuj:
            1 / 0
        wyjąwszy ZeroDivisionError jako e:
            exc = e

        self.adapter.exception('exc_info test', exc_info=exc)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.exc_info,
                         (exc.__class__, exc, exc.__traceback__))

    def test_critical(self):
        msg = 'critical test! %r'
        self.adapter.critical(msg, self.recording)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.levelno, logging.CRITICAL)
        self.assertEqual(record.msg, msg)
        self.assertEqual(record.args, (self.recording,))

    def test_is_enabled_for(self):
        old_disable = self.adapter.logger.manager.disable
        self.adapter.logger.manager.disable = 33
        self.addCleanup(setattr, self.adapter.logger.manager, 'disable',
                        old_disable)
        self.assertNieprawda(self.adapter.isEnabledFor(32))

    def test_has_handlers(self):
        self.assertPrawda(self.adapter.hasHandlers())

        dla handler w self.logger.handlers:
            self.logger.removeHandler(handler)

        self.assertNieprawda(self.logger.hasHandlers())
        self.assertNieprawda(self.adapter.hasHandlers())


klasa LoggerTest(BaseTest):

    def setUp(self):
        super(LoggerTest, self).setUp()
        self.recording = RecordingHandler()
        self.logger = logging.Logger(name='blah')
        self.logger.addHandler(self.recording)
        self.addCleanup(self.logger.removeHandler, self.recording)
        self.addCleanup(self.recording.close)
        self.addCleanup(logging.shutdown)

    def test_set_invalid_level(self):
        self.assertRaises(TypeError, self.logger.setLevel, object())

    def test_exception(self):
        msg = 'testing exception: %r'
        exc = Nic
        spróbuj:
            1 / 0
        wyjąwszy ZeroDivisionError jako e:
            exc = e
            self.logger.exception(msg, self.recording)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.levelno, logging.ERROR)
        self.assertEqual(record.msg, msg)
        self.assertEqual(record.args, (self.recording,))
        self.assertEqual(record.exc_info,
                         (exc.__class__, exc, exc.__traceback__))

    def test_log_invalid_level_with_raise(self):
        przy support.swap_attr(logging, 'raiseExceptions', Prawda):
            self.assertRaises(TypeError, self.logger.log, '10', 'test message')

    def test_log_invalid_level_no_raise(self):
        przy support.swap_attr(logging, 'raiseExceptions', Nieprawda):
            self.logger.log('10', 'test message')  # no exception happens

    def test_find_caller_with_stack_info(self):
        called = []
        support.patch(self, logging.traceback, 'print_stack',
                      lambda f, file: called.append(file.getvalue()))

        self.logger.findCaller(stack_info=Prawda)

        self.assertEqual(len(called), 1)
        self.assertEqual('Stack (most recent call last):\n', called[0])

    def test_make_record_with_extra_overwrite(self):
        name = 'my record'
        level = 13
        fn = lno = msg = args = exc_info = func = sinfo = Nic
        rv = logging._logRecordFactory(name, level, fn, lno, msg, args,
                                       exc_info, func, sinfo)

        dla key w ('message', 'asctime') + tuple(rv.__dict__.keys()):
            extra = {key: 'some value'}
            self.assertRaises(KeyError, self.logger.makeRecord, name, level,
                              fn, lno, msg, args, exc_info,
                              extra=extra, sinfo=sinfo)

    def test_make_record_with_extra_no_overwrite(self):
        name = 'my record'
        level = 13
        fn = lno = msg = args = exc_info = func = sinfo = Nic
        extra = {'valid_key': 'some value'}
        result = self.logger.makeRecord(name, level, fn, lno, msg, args,
                                        exc_info, extra=extra, sinfo=sinfo)
        self.assertIn('valid_key', result.__dict__)

    def test_has_handlers(self):
        self.assertPrawda(self.logger.hasHandlers())

        dla handler w self.logger.handlers:
            self.logger.removeHandler(handler)
        self.assertNieprawda(self.logger.hasHandlers())

    def test_has_handlers_no_propagate(self):
        child_logger = logging.getLogger('blah.child')
        child_logger.propagate = Nieprawda
        self.assertNieprawda(child_logger.hasHandlers())

    def test_is_enabled_for(self):
        old_disable = self.logger.manager.disable
        self.logger.manager.disable = 23
        self.addCleanup(setattr, self.logger.manager, 'disable', old_disable)
        self.assertNieprawda(self.logger.isEnabledFor(22))

    def test_root_logger_aliases(self):
        root = logging.getLogger()
        self.assertIs(root, logging.root)
        self.assertIs(root, logging.getLogger(Nic))
        self.assertIs(root, logging.getLogger(''))
        self.assertIs(root, logging.getLogger('foo').root)
        self.assertIs(root, logging.getLogger('foo.bar').root)
        self.assertIs(root, logging.getLogger('foo').parent)

        self.assertIsNot(root, logging.getLogger('\0'))
        self.assertIsNot(root, logging.getLogger('foo.bar').parent)

    def test_invalid_names(self):
        self.assertRaises(TypeError, logging.getLogger, any)
        self.assertRaises(TypeError, logging.getLogger, b'foo')


klasa BaseFileTest(BaseTest):
    "Base klasa dla handler tests that write log files"

    def setUp(self):
        BaseTest.setUp(self)
        fd, self.fn = tempfile.mkstemp(".log", "test_logging-2-")
        os.close(fd)
        self.rmfiles = []

    def tearDown(self):
        dla fn w self.rmfiles:
            os.unlink(fn)
        jeżeli os.path.exists(self.fn):
            os.unlink(self.fn)
        BaseTest.tearDown(self)

    def assertLogFile(self, filename):
        "Assert a log file jest there oraz register it dla deletion"
        self.assertPrawda(os.path.exists(filename),
                        msg="Log file %r does nie exist" % filename)
        self.rmfiles.append(filename)


klasa FileHandlerTest(BaseFileTest):
    def test_delay(self):
        os.unlink(self.fn)
        fh = logging.FileHandler(self.fn, delay=Prawda)
        self.assertIsNic(fh.stream)
        self.assertNieprawda(os.path.exists(self.fn))
        fh.handle(logging.makeLogRecord({}))
        self.assertIsNotNic(fh.stream)
        self.assertPrawda(os.path.exists(self.fn))
        fh.close()

klasa RotatingFileHandlerTest(BaseFileTest):
    def next_rec(self):
        zwróć logging.LogRecord('n', logging.DEBUG, 'p', 1,
                                 self.next_message(), Nic, Nic, Nic)

    def test_should_not_rollover(self):
        # If maxbytes jest zero rollover never occurs
        rh = logging.handlers.RotatingFileHandler(self.fn, maxBytes=0)
        self.assertNieprawda(rh.shouldRollover(Nic))
        rh.close()

    def test_should_rollover(self):
        rh = logging.handlers.RotatingFileHandler(self.fn, maxBytes=1)
        self.assertPrawda(rh.shouldRollover(self.next_rec()))
        rh.close()

    def test_file_created(self):
        # checks that the file jest created oraz assumes it was created
        # by us
        rh = logging.handlers.RotatingFileHandler(self.fn)
        rh.emit(self.next_rec())
        self.assertLogFile(self.fn)
        rh.close()

    def test_rollover_filenames(self):
        def namer(name):
            zwróć name + ".test"
        rh = logging.handlers.RotatingFileHandler(
            self.fn, backupCount=2, maxBytes=1)
        rh.namer = namer
        rh.emit(self.next_rec())
        self.assertLogFile(self.fn)
        rh.emit(self.next_rec())
        self.assertLogFile(namer(self.fn + ".1"))
        rh.emit(self.next_rec())
        self.assertLogFile(namer(self.fn + ".2"))
        self.assertNieprawda(os.path.exists(namer(self.fn + ".3")))
        rh.close()

    @support.requires_zlib
    def test_rotator(self):
        def namer(name):
            zwróć name + ".gz"

        def rotator(source, dest):
            przy open(source, "rb") jako sf:
                data = sf.read()
                compressed = zlib.compress(data, 9)
                przy open(dest, "wb") jako df:
                    df.write(compressed)
            os.remove(source)

        rh = logging.handlers.RotatingFileHandler(
            self.fn, backupCount=2, maxBytes=1)
        rh.rotator = rotator
        rh.namer = namer
        m1 = self.next_rec()
        rh.emit(m1)
        self.assertLogFile(self.fn)
        m2 = self.next_rec()
        rh.emit(m2)
        fn = namer(self.fn + ".1")
        self.assertLogFile(fn)
        newline = os.linesep
        przy open(fn, "rb") jako f:
            compressed = f.read()
            data = zlib.decompress(compressed)
            self.assertEqual(data.decode("ascii"), m1.msg + newline)
        rh.emit(self.next_rec())
        fn = namer(self.fn + ".2")
        self.assertLogFile(fn)
        przy open(fn, "rb") jako f:
            compressed = f.read()
            data = zlib.decompress(compressed)
            self.assertEqual(data.decode("ascii"), m1.msg + newline)
        rh.emit(self.next_rec())
        fn = namer(self.fn + ".2")
        przy open(fn, "rb") jako f:
            compressed = f.read()
            data = zlib.decompress(compressed)
            self.assertEqual(data.decode("ascii"), m2.msg + newline)
        self.assertNieprawda(os.path.exists(namer(self.fn + ".3")))
        rh.close()

klasa TimedRotatingFileHandlerTest(BaseFileTest):
    # other test methods added below
    def test_rollover(self):
        fh = logging.handlers.TimedRotatingFileHandler(self.fn, 'S',
                                                       backupCount=1)
        fmt = logging.Formatter('%(asctime)s %(message)s')
        fh.setFormatter(fmt)
        r1 = logging.makeLogRecord({'msg': 'testing - initial'})
        fh.emit(r1)
        self.assertLogFile(self.fn)
        time.sleep(1.1)    # a little over a second ...
        r2 = logging.makeLogRecord({'msg': 'testing - after delay'})
        fh.emit(r2)
        fh.close()
        # At this point, we should have a recent rotated file which we
        # can test dla the existence of. However, w practice, on some
        # machines which run really slowly, we don't know how far back
        # w time to go to look dla the log file. So, we go back a fair
        # bit, oraz stop jako soon jako we see a rotated file. In theory this
        # could of course still fail, but the chances are lower.
        found = Nieprawda
        now = datetime.datetime.now()
        GO_BACK = 5 * 60 # seconds
        dla secs w range(GO_BACK):
            prev = now - datetime.timedelta(seconds=secs)
            fn = self.fn + prev.strftime(".%Y-%m-%d_%H-%M-%S")
            found = os.path.exists(fn)
            jeżeli found:
                self.rmfiles.append(fn)
                przerwij
        msg = 'No rotated files found, went back %d seconds' % GO_BACK
        jeżeli nie found:
            #print additional diagnostics
            dn, fn = os.path.split(self.fn)
            files = [f dla f w os.listdir(dn) jeżeli f.startswith(fn)]
            print('Test time: %s' % now.strftime("%Y-%m-%d %H-%M-%S"), file=sys.stderr)
            print('The only matching files are: %s' % files, file=sys.stderr)
            dla f w files:
                print('Contents of %s:' % f)
                path = os.path.join(dn, f)
                przy open(path, 'r') jako tf:
                    print(tf.read())
        self.assertPrawda(found, msg=msg)

    def test_invalid(self):
        assertRaises = self.assertRaises
        assertRaises(ValueError, logging.handlers.TimedRotatingFileHandler,
                     self.fn, 'X', delay=Prawda)
        assertRaises(ValueError, logging.handlers.TimedRotatingFileHandler,
                     self.fn, 'W', delay=Prawda)
        assertRaises(ValueError, logging.handlers.TimedRotatingFileHandler,
                     self.fn, 'W7', delay=Prawda)

    def test_compute_rollover_daily_attime(self):
        currentTime = 0
        atTime = datetime.time(12, 0, 0)
        rh = logging.handlers.TimedRotatingFileHandler(
            self.fn, when='MIDNIGHT', interval=1, backupCount=0, utc=Prawda,
            atTime=atTime)
        spróbuj:
            actual = rh.computeRollover(currentTime)
            self.assertEqual(actual, currentTime + 12 * 60 * 60)

            actual = rh.computeRollover(currentTime + 13 * 60 * 60)
            self.assertEqual(actual, currentTime + 36 * 60 * 60)
        w_końcu:
            rh.close()

    #@unittest.skipIf(Prawda, 'Temporarily skipped dopóki failures investigated.')
    def test_compute_rollover_weekly_attime(self):
        currentTime = int(time.time())
        today = currentTime - currentTime % 86400

        atTime = datetime.time(12, 0, 0)

        wday = time.gmtime(today).tm_wday
        dla day w range(7):
            rh = logging.handlers.TimedRotatingFileHandler(
                self.fn, when='W%d' % day, interval=1, backupCount=0, utc=Prawda,
                atTime=atTime)
            spróbuj:
                jeżeli wday > day:
                    # The rollover day has already dalejed this week, so we
                    # go over into next week
                    expected = (7 - wday + day)
                inaczej:
                    expected = (day - wday)
                # At this point expected jest w days z now, convert to seconds
                expected *= 24 * 60 * 60
                # Add w the rollover time
                expected += 12 * 60 * 60
                # Add w adjustment dla today
                expected += today
                actual = rh.computeRollover(today)
                jeżeli actual != expected:
                    print('failed w timezone: %d' % time.timezone)
                    print('local vars: %s' % locals())
                self.assertEqual(actual, expected)
                jeżeli day == wday:
                    # goes into following week
                    expected += 7 * 24 * 60 * 60
                actual = rh.computeRollover(today + 13 * 60 * 60)
                jeżeli actual != expected:
                    print('failed w timezone: %d' % time.timezone)
                    print('local vars: %s' % locals())
                self.assertEqual(actual, expected)
            w_końcu:
                rh.close()


def secs(**kw):
    zwróć datetime.timedelta(**kw) // datetime.timedelta(seconds=1)

dla when, exp w (('S', 1),
                  ('M', 60),
                  ('H', 60 * 60),
                  ('D', 60 * 60 * 24),
                  ('MIDNIGHT', 60 * 60 * 24),
                  # current time (epoch start) jest a Thursday, W0 means Monday
                  ('W0', secs(days=4, hours=24)),
                 ):
    def test_compute_rollover(self, when=when, exp=exp):
        rh = logging.handlers.TimedRotatingFileHandler(
            self.fn, when=when, interval=1, backupCount=0, utc=Prawda)
        currentTime = 0.0
        actual = rh.computeRollover(currentTime)
        jeżeli exp != actual:
            # Failures occur on some systems dla MIDNIGHT oraz W0.
            # Print detailed calculation dla MIDNIGHT so we can try to see
            # what's going on
            jeżeli when == 'MIDNIGHT':
                spróbuj:
                    jeżeli rh.utc:
                        t = time.gmtime(currentTime)
                    inaczej:
                        t = time.localtime(currentTime)
                    currentHour = t[3]
                    currentMinute = t[4]
                    currentSecond = t[5]
                    # r jest the number of seconds left between now oraz midnight
                    r = logging.handlers._MIDNIGHT - ((currentHour * 60 +
                                                       currentMinute) * 60 +
                            currentSecond)
                    result = currentTime + r
                    print('t: %s (%s)' % (t, rh.utc), file=sys.stderr)
                    print('currentHour: %s' % currentHour, file=sys.stderr)
                    print('currentMinute: %s' % currentMinute, file=sys.stderr)
                    print('currentSecond: %s' % currentSecond, file=sys.stderr)
                    print('r: %s' % r, file=sys.stderr)
                    print('result: %s' % result, file=sys.stderr)
                wyjąwszy Exception:
                    print('exception w diagnostic code: %s' % sys.exc_info()[1], file=sys.stderr)
        self.assertEqual(exp, actual)
        rh.close()
    setattr(TimedRotatingFileHandlerTest, "test_compute_rollover_%s" % when, test_compute_rollover)


@unittest.skipUnless(win32evtlog, 'win32evtlog/win32evtlogutil required dla this test.')
klasa NTEventLogHandlerTest(BaseTest):
    def test_basic(self):
        logtype = 'Application'
        elh = win32evtlog.OpenEventLog(Nic, logtype)
        num_recs = win32evtlog.GetNumberOfEventLogRecords(elh)
        h = logging.handlers.NTEventLogHandler('test_logging')
        r = logging.makeLogRecord({'msg': 'Test Log Message'})
        h.handle(r)
        h.close()
        # Now see jeżeli the event jest recorded
        self.assertLess(num_recs, win32evtlog.GetNumberOfEventLogRecords(elh))
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | \
                win32evtlog.EVENTLOG_SEQUENTIAL_READ
        found = Nieprawda
        GO_BACK = 100
        events = win32evtlog.ReadEventLog(elh, flags, GO_BACK)
        dla e w events:
            jeżeli e.SourceName != 'test_logging':
                kontynuuj
            msg = win32evtlogutil.SafeFormatMessage(e, logtype)
            jeżeli msg != 'Test Log Message\r\n':
                kontynuuj
            found = Prawda
            przerwij
        msg = 'Record nie found w event log, went back %d records' % GO_BACK
        self.assertPrawda(found, msg=msg)

# Set the locale to the platform-dependent default.  I have no idea
# why the test does this, but w any case we save the current locale
# first oraz restore it at the end.
@support.run_with_locale('LC_ALL', '')
def test_main():
    support.run_unittest(
        BuiltinLevelsTest, BasicFilterTest, CustomLevelsAndFiltersTest,
        HandlerTest, MemoryHandlerTest, ConfigFileTest, SocketHandlerTest,
        DatagramHandlerTest, MemoryTest, EncodingTest, WarningsTest,
        ConfigDictTest, ManagerTest, FormatterTest, BufferingFormatterTest,
        StreamHandlerTest, LogRecordFactoryTest, ChildLoggerTest,
        QueueHandlerTest, ShutdownTest, ModuleLevelMiscTest, BasicConfigTest,
        LoggerAdapterTest, LoggerTest, SMTPHandlerTest, FileHandlerTest,
        RotatingFileHandlerTest,  LastResortTest, LogRecordTest,
        ExceptionTest, SysLogHandlerTest, HTTPHandlerTest,
        NTEventLogHandlerTest, TimedRotatingFileHandlerTest,
        UnixSocketHandlerTest, UnixDatagramHandlerTest, UnixSysLogHandlerTest)

jeżeli __name__ == "__main__":
    test_main()
