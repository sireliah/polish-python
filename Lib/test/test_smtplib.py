zaimportuj asyncore
zaimportuj email.mime.text
z email.message zaimportuj EmailMessage
z email.base64mime zaimportuj body_encode jako encode_base64
zaimportuj email.utils
zaimportuj socket
zaimportuj smtpd
zaimportuj smtplib
zaimportuj io
zaimportuj re
zaimportuj sys
zaimportuj time
zaimportuj select
zaimportuj errno
zaimportuj textwrap

zaimportuj unittest
z test zaimportuj support, mock_socket

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

HOST = support.HOST

jeżeli sys.platform == 'darwin':
    # select.poll returns a select.POLLHUP at the end of the tests
    # on darwin, so just ignore it
    def handle_expt(self):
        dalej
    smtpd.SMTPChannel.handle_expt = handle_expt


def server(evt, buf, serv):
    serv.listen()
    evt.set()
    spróbuj:
        conn, addr = serv.accept()
    wyjąwszy socket.timeout:
        dalej
    inaczej:
        n = 500
        dopóki buf oraz n > 0:
            r, w, e = select.select([], [conn], [])
            jeżeli w:
                sent = conn.send(buf)
                buf = buf[sent:]

            n -= 1

        conn.close()
    w_końcu:
        serv.close()
        evt.set()

klasa GeneralTests(unittest.TestCase):

    def setUp(self):
        smtplib.socket = mock_socket
        self.port = 25

    def tearDown(self):
        smtplib.socket = socket

    # This method jest no longer used but jest retained dla backward compatibility,
    # so test to make sure it still works.
    def testQuoteData(self):
        teststr  = "abc\n.jkl\rfoo\r\n..blue"
        expected = "abc\r\n..jkl\r\nfoo\r\n...blue"
        self.assertEqual(expected, smtplib.quotedata(teststr))

    def testBasic1(self):
        mock_socket.reply_with(b"220 Hola mundo")
        # connects
        smtp = smtplib.SMTP(HOST, self.port)
        smtp.close()

    def testSourceAddress(self):
        mock_socket.reply_with(b"220 Hola mundo")
        # connects
        smtp = smtplib.SMTP(HOST, self.port,
                source_address=('127.0.0.1',19876))
        self.assertEqual(smtp.source_address, ('127.0.0.1', 19876))
        smtp.close()

    def testBasic2(self):
        mock_socket.reply_with(b"220 Hola mundo")
        # connects, include port w host name
        smtp = smtplib.SMTP("%s:%s" % (HOST, self.port))
        smtp.close()

    def testLocalHostName(self):
        mock_socket.reply_with(b"220 Hola mundo")
        # check that supplied local_hostname jest used
        smtp = smtplib.SMTP(HOST, self.port, local_hostname="testhost")
        self.assertEqual(smtp.local_hostname, "testhost")
        smtp.close()

    def testTimeoutDefault(self):
        mock_socket.reply_with(b"220 Hola mundo")
        self.assertIsNic(mock_socket.getdefaulttimeout())
        mock_socket.setdefaulttimeout(30)
        self.assertEqual(mock_socket.getdefaulttimeout(), 30)
        spróbuj:
            smtp = smtplib.SMTP(HOST, self.port)
        w_końcu:
            mock_socket.setdefaulttimeout(Nic)
        self.assertEqual(smtp.sock.gettimeout(), 30)
        smtp.close()

    def testTimeoutNic(self):
        mock_socket.reply_with(b"220 Hola mundo")
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            smtp = smtplib.SMTP(HOST, self.port, timeout=Nic)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertIsNic(smtp.sock.gettimeout())
        smtp.close()

    def testTimeoutValue(self):
        mock_socket.reply_with(b"220 Hola mundo")
        smtp = smtplib.SMTP(HOST, self.port, timeout=30)
        self.assertEqual(smtp.sock.gettimeout(), 30)
        smtp.close()

    def test_debuglevel(self):
        mock_socket.reply_with(b"220 Hello world")
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(1)
        przy support.captured_stderr() jako stderr:
            smtp.connect(HOST, self.port)
        smtp.close()
        expected = re.compile(r"^connect:", re.MULTILINE)
        self.assertRegex(stderr.getvalue(), expected)

    def test_debuglevel_2(self):
        mock_socket.reply_with(b"220 Hello world")
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(2)
        przy support.captured_stderr() jako stderr:
            smtp.connect(HOST, self.port)
        smtp.close()
        expected = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{6} connect: ",
                              re.MULTILINE)
        self.assertRegex(stderr.getvalue(), expected)


# Test server thread using the specified SMTP server class
def debugging_server(serv, serv_evt, client_evt):
    serv_evt.set()

    spróbuj:
        jeżeli hasattr(select, 'poll'):
            poll_fun = asyncore.poll2
        inaczej:
            poll_fun = asyncore.poll

        n = 1000
        dopóki asyncore.socket_map oraz n > 0:
            poll_fun(0.01, asyncore.socket_map)

            # when the client conversation jest finished, it will
            # set client_evt, oraz it's then ok to kill the server
            jeżeli client_evt.is_set():
                serv.close()
                przerwij

            n -= 1

    wyjąwszy socket.timeout:
        dalej
    w_końcu:
        jeżeli nie client_evt.is_set():
            # allow some time dla the client to read the result
            time.sleep(0.5)
            serv.close()
        asyncore.close_all()
        serv_evt.set()

MSG_BEGIN = '---------- MESSAGE FOLLOWS ----------\n'
MSG_END = '------------ END MESSAGE ------------\n'

# NOTE: Some SMTP objects w the tests below are created przy a non-default
# local_hostname argument to the constructor, since (on some systems) the FQDN
# lookup caused by the default local_hostname sometimes takes so long that the
# test server times out, causing the test to fail.

# Test behavior of smtpd.DebuggingServer
@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa DebuggingServerTests(unittest.TestCase):

    maxDiff = Nic

    def setUp(self):
        self.real_getfqdn = socket.getfqdn
        socket.getfqdn = mock_socket.getfqdn
        # temporarily replace sys.stdout to capture DebuggingServer output
        self.old_stdout = sys.stdout
        self.output = io.StringIO()
        sys.stdout = self.output

        self.serv_evt = threading.Event()
        self.client_evt = threading.Event()
        # Capture SMTPChannel debug output
        self.old_DEBUGSTREAM = smtpd.DEBUGSTREAM
        smtpd.DEBUGSTREAM = io.StringIO()
        # Pick a random unused port by dalejing 0 dla the port number
        self.serv = smtpd.DebuggingServer((HOST, 0), ('nowhere', -1),
                                          decode_data=Prawda)
        # Keep a note of what port was assigned
        self.port = self.serv.socket.getsockname()[1]
        serv_args = (self.serv, self.serv_evt, self.client_evt)
        self.thread = threading.Thread(target=debugging_server, args=serv_args)
        self.thread.start()

        # wait until server thread has assigned a port number
        self.serv_evt.wait()
        self.serv_evt.clear()

    def tearDown(self):
        socket.getfqdn = self.real_getfqdn
        # indicate that the client jest finished
        self.client_evt.set()
        # wait dla the server thread to terminate
        self.serv_evt.wait()
        self.thread.join()
        # restore sys.stdout
        sys.stdout = self.old_stdout
        # restore DEBUGSTREAM
        smtpd.DEBUGSTREAM.close()
        smtpd.DEBUGSTREAM = self.old_DEBUGSTREAM

    def testBasic(self):
        # connect
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.quit()

    def testSourceAddress(self):
        # connect
        port = support.find_unused_port()
        spróbuj:
            smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost',
                    timeout=3, source_address=('127.0.0.1', port))
            self.assertEqual(smtp.source_address, ('127.0.0.1', port))
            self.assertEqual(smtp.local_hostname, 'localhost')
            smtp.quit()
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.EADDRINUSE:
                self.skipTest("couldn't bind to port %d" % port)
            podnieś

    def testNOOP(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        expected = (250, b'OK')
        self.assertEqual(smtp.noop(), expected)
        smtp.quit()

    def testRSET(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        expected = (250, b'OK')
        self.assertEqual(smtp.rset(), expected)
        smtp.quit()

    def testELHO(self):
        # EHLO isn't implemented w DebuggingServer
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        expected = (250, b'\nSIZE 33554432\nHELP')
        self.assertEqual(smtp.ehlo(), expected)
        smtp.quit()

    def testEXPNNotImplemented(self):
        # EXPN isn't implemented w DebuggingServer
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        expected = (502, b'EXPN nie implemented')
        smtp.putcmd('EXPN')
        self.assertEqual(smtp.getreply(), expected)
        smtp.quit()

    def testVRFY(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        expected = (252, b'Cannot VRFY user, but will accept message ' + \
                         b'and attempt delivery')
        self.assertEqual(smtp.vrfy('nobody@nowhere.com'), expected)
        self.assertEqual(smtp.verify('nobody@nowhere.com'), expected)
        smtp.quit()

    def testSecondHELO(self):
        # check that a second HELO returns a message that it's a duplicate
        # (this behavior jest specific to smtpd.SMTPChannel)
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.helo()
        expected = (503, b'Duplicate HELO/EHLO')
        self.assertEqual(smtp.helo(), expected)
        smtp.quit()

    def testHELP(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        self.assertEqual(smtp.help(), b'Supported commands: EHLO HELO MAIL ' + \
                                      b'RCPT DATA RSET NOOP QUIT VRFY')
        smtp.quit()

    def testSend(self):
        # connect oraz send mail
        m = 'A test message'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.sendmail('John', 'Sally', m)
        # XXX(nnorwitz): this test jest flaky oraz dies przy a bad file descriptor
        # w asyncore.  This sleep might help, but should really be fixed
        # properly by using an Event variable.
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m, MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)

    def testSendBinary(self):
        m = b'A test message'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.sendmail('John', 'Sally', m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.decode('ascii'), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)

    def testSendNeedingDotQuote(self):
        # Issue 12283
        m = '.A test\n.mes.sage.'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.sendmail('John', 'Sally', m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m, MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)

    def testSendNullSender(self):
        m = 'A test message'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.sendmail('<>', 'Sally', m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m, MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)
        debugout = smtpd.DEBUGSTREAM.getvalue()
        sender = re.compile("^sender: <>$", re.MULTILINE)
        self.assertRegex(debugout, sender)

    def testSendMessage(self):
        m = email.mime.text.MIMEText('A test message')
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.send_message(m, from_addr='John', to_addrs='Sally')
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        # Add the X-Peer header that DebuggingServer adds
        m['X-Peer'] = socket.gethostbyname('localhost')
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.as_string(), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)

    def testSendMessageWithAddresses(self):
        m = email.mime.text.MIMEText('A test message')
        m['From'] = 'foo@bar.com'
        m['To'] = 'John'
        m['CC'] = 'Sally, Fred'
        m['Bcc'] = 'John Root <root@localhost>, "Dinsdale" <warped@silly.walks.com>'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.send_message(m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()
        # make sure the Bcc header jest still w the message.
        self.assertEqual(m['Bcc'], 'John Root <root@localhost>, "Dinsdale" '
                                    '<warped@silly.walks.com>')

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        # Add the X-Peer header that DebuggingServer adds
        m['X-Peer'] = socket.gethostbyname('localhost')
        # The Bcc header should nie be transmitted.
        usuń m['Bcc']
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.as_string(), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)
        debugout = smtpd.DEBUGSTREAM.getvalue()
        sender = re.compile("^sender: foo@bar.com$", re.MULTILINE)
        self.assertRegex(debugout, sender)
        dla addr w ('John', 'Sally', 'Fred', 'root@localhost',
                     'warped@silly.walks.com'):
            to_addr = re.compile(r"^recips: .*'{}'.*$".format(addr),
                                 re.MULTILINE)
            self.assertRegex(debugout, to_addr)

    def testSendMessageWithSomeAddresses(self):
        # Make sure nothing przerwijs jeżeli nie all of the three 'to' headers exist
        m = email.mime.text.MIMEText('A test message')
        m['From'] = 'foo@bar.com'
        m['To'] = 'John, Dinsdale'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.send_message(m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        # Add the X-Peer header that DebuggingServer adds
        m['X-Peer'] = socket.gethostbyname('localhost')
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.as_string(), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)
        debugout = smtpd.DEBUGSTREAM.getvalue()
        sender = re.compile("^sender: foo@bar.com$", re.MULTILINE)
        self.assertRegex(debugout, sender)
        dla addr w ('John', 'Dinsdale'):
            to_addr = re.compile(r"^recips: .*'{}'.*$".format(addr),
                                 re.MULTILINE)
            self.assertRegex(debugout, to_addr)

    def testSendMessageWithSpecifiedAddresses(self):
        # Make sure addresses specified w call override those w message.
        m = email.mime.text.MIMEText('A test message')
        m['From'] = 'foo@bar.com'
        m['To'] = 'John, Dinsdale'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.send_message(m, from_addr='joe@example.com', to_addrs='foo@example.net')
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        # Add the X-Peer header that DebuggingServer adds
        m['X-Peer'] = socket.gethostbyname('localhost')
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.as_string(), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)
        debugout = smtpd.DEBUGSTREAM.getvalue()
        sender = re.compile("^sender: joe@example.com$", re.MULTILINE)
        self.assertRegex(debugout, sender)
        dla addr w ('John', 'Dinsdale'):
            to_addr = re.compile(r"^recips: .*'{}'.*$".format(addr),
                                 re.MULTILINE)
            self.assertNotRegex(debugout, to_addr)
        recip = re.compile(r"^recips: .*'foo@example.net'.*$", re.MULTILINE)
        self.assertRegex(debugout, recip)

    def testSendMessageWithMultipleFrom(self):
        # Sender overrides To
        m = email.mime.text.MIMEText('A test message')
        m['From'] = 'Bernard, Bianca'
        m['Sender'] = 'the_rescuers@Rescue-Aid-Society.com'
        m['To'] = 'John, Dinsdale'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.send_message(m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        # Add the X-Peer header that DebuggingServer adds
        m['X-Peer'] = socket.gethostbyname('localhost')
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.as_string(), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)
        debugout = smtpd.DEBUGSTREAM.getvalue()
        sender = re.compile("^sender: the_rescuers@Rescue-Aid-Society.com$", re.MULTILINE)
        self.assertRegex(debugout, sender)
        dla addr w ('John', 'Dinsdale'):
            to_addr = re.compile(r"^recips: .*'{}'.*$".format(addr),
                                 re.MULTILINE)
            self.assertRegex(debugout, to_addr)

    def testSendMessageResent(self):
        m = email.mime.text.MIMEText('A test message')
        m['From'] = 'foo@bar.com'
        m['To'] = 'John'
        m['CC'] = 'Sally, Fred'
        m['Bcc'] = 'John Root <root@localhost>, "Dinsdale" <warped@silly.walks.com>'
        m['Resent-Date'] = 'Thu, 1 Jan 1970 17:42:00 +0000'
        m['Resent-From'] = 'holy@grail.net'
        m['Resent-To'] = 'Martha <my_mom@great.cooker.com>, Jeff'
        m['Resent-Bcc'] = 'doe@losthope.net'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        smtp.send_message(m)
        # XXX (see comment w testSend)
        time.sleep(0.01)
        smtp.quit()

        self.client_evt.set()
        self.serv_evt.wait()
        self.output.flush()
        # The Resent-Bcc headers are deleted before serialization.
        usuń m['Bcc']
        usuń m['Resent-Bcc']
        # Add the X-Peer header that DebuggingServer adds
        m['X-Peer'] = socket.gethostbyname('localhost')
        mexpect = '%s%s\n%s' % (MSG_BEGIN, m.as_string(), MSG_END)
        self.assertEqual(self.output.getvalue(), mexpect)
        debugout = smtpd.DEBUGSTREAM.getvalue()
        sender = re.compile("^sender: holy@grail.net$", re.MULTILINE)
        self.assertRegex(debugout, sender)
        dla addr w ('my_mom@great.cooker.com', 'Jeff', 'doe@losthope.net'):
            to_addr = re.compile(r"^recips: .*'{}'.*$".format(addr),
                                 re.MULTILINE)
            self.assertRegex(debugout, to_addr)

    def testSendMessageMultipleResentRaises(self):
        m = email.mime.text.MIMEText('A test message')
        m['From'] = 'foo@bar.com'
        m['To'] = 'John'
        m['CC'] = 'Sally, Fred'
        m['Bcc'] = 'John Root <root@localhost>, "Dinsdale" <warped@silly.walks.com>'
        m['Resent-Date'] = 'Thu, 1 Jan 1970 17:42:00 +0000'
        m['Resent-From'] = 'holy@grail.net'
        m['Resent-To'] = 'Martha <my_mom@great.cooker.com>, Jeff'
        m['Resent-Bcc'] = 'doe@losthope.net'
        m['Resent-Date'] = 'Thu, 2 Jan 1970 17:42:00 +0000'
        m['Resent-To'] = 'holy@grail.net'
        m['Resent-From'] = 'Martha <my_mom@great.cooker.com>, Jeff'
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=3)
        przy self.assertRaises(ValueError):
            smtp.send_message(m)
        smtp.close()

klasa NonConnectingTests(unittest.TestCase):

    def testNotConnected(self):
        # Test various operations on an unconnected SMTP object that
        # should podnieś exceptions (at present the attempt w SMTP.send
        # to reference the nonexistent 'sock' attribute of the SMTP object
        # causes an AttributeError)
        smtp = smtplib.SMTP()
        self.assertRaises(smtplib.SMTPServerDisconnected, smtp.ehlo)
        self.assertRaises(smtplib.SMTPServerDisconnected,
                          smtp.send, 'test msg')

    def testNonnumericPort(self):
        # check that non-numeric port podnieśs OSError
        self.assertRaises(OSError, smtplib.SMTP,
                          "localhost", "bogus")
        self.assertRaises(OSError, smtplib.SMTP,
                          "localhost:bogus")


# test response of client to a non-successful HELO message
@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa BadHELOServerTests(unittest.TestCase):

    def setUp(self):
        smtplib.socket = mock_socket
        mock_socket.reply_with(b"199 no hello dla you!")
        self.old_stdout = sys.stdout
        self.output = io.StringIO()
        sys.stdout = self.output
        self.port = 25

    def tearDown(self):
        smtplib.socket = socket
        sys.stdout = self.old_stdout

    def testFailingHELO(self):
        self.assertRaises(smtplib.SMTPConnectError, smtplib.SMTP,
                            HOST, self.port, 'localhost', 3)


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa TooLongLineTests(unittest.TestCase):
    respdata = b'250 OK' + (b'.' * smtplib._MAXLINE * 2) + b'\n'

    def setUp(self):
        self.old_stdout = sys.stdout
        self.output = io.StringIO()
        sys.stdout = self.output

        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.port = support.bind_port(self.sock)
        servargs = (self.evt, self.respdata, self.sock)
        threading.Thread(target=server, args=servargs).start()
        self.evt.wait()
        self.evt.clear()

    def tearDown(self):
        self.evt.wait()
        sys.stdout = self.old_stdout

    def testLineTooLong(self):
        self.assertRaises(smtplib.SMTPResponseException, smtplib.SMTP,
                          HOST, self.port, 'localhost', 3)


sim_users = {'Mr.A@somewhere.com':'John A',
             'Ms.B@xn--fo-fka.com':'Sally B',
             'Mrs.C@somewhereesle.com':'Ruth C',
            }

sim_auth = ('Mr.A@somewhere.com', 'somepassword')
sim_cram_md5_challenge = ('PENCeUxFREJoU0NnbmhNWitOMjNGNn'
                          'dAZWx3b29kLmlubm9zb2Z0LmNvbT4=')
sim_auth_credentials = {
    'login': 'TXIuQUBzb21ld2hlcmUuY29t',
    'plain': 'AE1yLkFAc29tZXdoZXJlLmNvbQBzb21lcGFzc3dvcmQ=',
    'cram-md5': ('TXIUQUBZB21LD2HLCMUUY29TIDG4OWQ0MJ'
                 'KWZGQ4ODNMNDA4NTGXMDRLZWMYZJDMODG1'),
    }
sim_auth_login_user = 'TXIUQUBZB21LD2HLCMUUY29T'
sim_auth_plain = 'AE1YLKFAC29TZXDOZXJLLMNVBQBZB21LCGFZC3DVCMQ='

sim_lists = {'list-1':['Mr.A@somewhere.com','Mrs.C@somewhereesle.com'],
             'list-2':['Ms.B@xn--fo-fka.com',],
            }

# Simulated SMTP channel & server
klasa SimSMTPChannel(smtpd.SMTPChannel):

    quit_response = Nic
    mail_response = Nic
    rcpt_response = Nic
    data_response = Nic
    rcpt_count = 0
    rset_count = 0
    disconnect = 0

    def __init__(self, extra_features, *args, **kw):
        self._extrafeatures = ''.join(
            [ "250-{0}\r\n".format(x) dla x w extra_features ])
        super(SimSMTPChannel, self).__init__(*args, **kw)

    def smtp_EHLO(self, arg):
        resp = ('250-testhost\r\n'
                '250-EXPN\r\n'
                '250-SIZE 20000000\r\n'
                '250-STARTTLS\r\n'
                '250-DELIVERBY\r\n')
        resp = resp + self._extrafeatures + '250 HELP'
        self.push(resp)
        self.seen_greeting = arg
        self.extended_smtp = Prawda

    def smtp_VRFY(self, arg):
        # For max compatibility smtplib should be sending the raw address.
        jeżeli arg w sim_users:
            self.push('250 %s %s' % (sim_users[arg], smtplib.quoteaddr(arg)))
        inaczej:
            self.push('550 No such user: %s' % arg)

    def smtp_EXPN(self, arg):
        list_name = arg.lower()
        jeżeli list_name w sim_lists:
            user_list = sim_lists[list_name]
            dla n, user_email w enumerate(user_list):
                quoted_addr = smtplib.quoteaddr(user_email)
                jeżeli n < len(user_list) - 1:
                    self.push('250-%s %s' % (sim_users[user_email], quoted_addr))
                inaczej:
                    self.push('250 %s %s' % (sim_users[user_email], quoted_addr))
        inaczej:
            self.push('550 No access dla you!')

    def smtp_AUTH(self, arg):
        mech = arg.strip().lower()
        jeżeli mech=='cram-md5':
            self.push('334 {}'.format(sim_cram_md5_challenge))
        albo_inaczej mech nie w sim_auth_credentials:
            self.push('504 auth type unimplemented')
            zwróć
        albo_inaczej mech=='plain':
            self.push('334 ')
        albo_inaczej mech=='login':
            self.push('334 ')
        inaczej:
            self.push('550 No access dla you!')

    def smtp_QUIT(self, arg):
        jeżeli self.quit_response jest Nic:
            super(SimSMTPChannel, self).smtp_QUIT(arg)
        inaczej:
            self.push(self.quit_response)
            self.close_when_done()

    def smtp_MAIL(self, arg):
        jeżeli self.mail_response jest Nic:
            super().smtp_MAIL(arg)
        inaczej:
            self.push(self.mail_response)
            jeżeli self.disconnect:
                self.close_when_done()

    def smtp_RCPT(self, arg):
        jeżeli self.rcpt_response jest Nic:
            super().smtp_RCPT(arg)
            zwróć
        self.rcpt_count += 1
        self.push(self.rcpt_response[self.rcpt_count-1])

    def smtp_RSET(self, arg):
        self.rset_count += 1
        super().smtp_RSET(arg)

    def smtp_DATA(self, arg):
        jeżeli self.data_response jest Nic:
            super().smtp_DATA(arg)
        inaczej:
            self.push(self.data_response)

    def handle_error(self):
        podnieś


klasa SimSMTPServer(smtpd.SMTPServer):

    channel_class = SimSMTPChannel

    def __init__(self, *args, **kw):
        self._extra_features = []
        smtpd.SMTPServer.__init__(self, *args, **kw)

    def handle_accepted(self, conn, addr):
        self._SMTPchannel = self.channel_class(
            self._extra_features, self, conn, addr,
            decode_data=self._decode_data)

    def process_message(self, peer, mailfrom, rcpttos, data):
        dalej

    def add_feature(self, feature):
        self._extra_features.append(feature)

    def handle_error(self):
        podnieś


# Test various SMTP & ESMTP commands/behaviors that require a simulated server
# (i.e., something przy more features than DebuggingServer)
@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SMTPSimTests(unittest.TestCase):

    def setUp(self):
        self.real_getfqdn = socket.getfqdn
        socket.getfqdn = mock_socket.getfqdn
        self.serv_evt = threading.Event()
        self.client_evt = threading.Event()
        # Pick a random unused port by dalejing 0 dla the port number
        self.serv = SimSMTPServer((HOST, 0), ('nowhere', -1), decode_data=Prawda)
        # Keep a note of what port was assigned
        self.port = self.serv.socket.getsockname()[1]
        serv_args = (self.serv, self.serv_evt, self.client_evt)
        self.thread = threading.Thread(target=debugging_server, args=serv_args)
        self.thread.start()

        # wait until server thread has assigned a port number
        self.serv_evt.wait()
        self.serv_evt.clear()

    def tearDown(self):
        socket.getfqdn = self.real_getfqdn
        # indicate that the client jest finished
        self.client_evt.set()
        # wait dla the server thread to terminate
        self.serv_evt.wait()
        self.thread.join()

    def testBasic(self):
        # smoke test
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        smtp.quit()

    def testEHLO(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)

        # no features should be present before the EHLO
        self.assertEqual(smtp.esmtp_features, {})

        # features expected z the test server
        expected_features = {'expn':'',
                             'size': '20000000',
                             'starttls': '',
                             'deliverby': '',
                             'help': '',
                             }

        smtp.ehlo()
        self.assertEqual(smtp.esmtp_features, expected_features)
        dla k w expected_features:
            self.assertPrawda(smtp.has_extn(k))
        self.assertNieprawda(smtp.has_extn('unsupported-feature'))
        smtp.quit()

    def testVRFY(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)

        dla addr_spec, name w sim_users.items():
            expected_known = (250, bytes('%s %s' %
                                         (name, smtplib.quoteaddr(addr_spec)),
                                         "ascii"))
            self.assertEqual(smtp.vrfy(addr_spec), expected_known)

        u = 'nobody@nowhere.com'
        expected_unknown = (550, ('No such user: %s' % u).encode('ascii'))
        self.assertEqual(smtp.vrfy(u), expected_unknown)
        smtp.quit()

    def testEXPN(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)

        dla listname, members w sim_lists.items():
            users = []
            dla m w members:
                users.append('%s %s' % (sim_users[m], smtplib.quoteaddr(m)))
            expected_known = (250, bytes('\n'.join(users), "ascii"))
            self.assertEqual(smtp.expn(listname), expected_known)

        u = 'PSU-Members-List'
        expected_unknown = (550, b'No access dla you!')
        self.assertEqual(smtp.expn(u), expected_unknown)
        smtp.quit()

    # SimSMTPChannel doesn't fully support AUTH because it requires a
    # synchronous read to obtain the credentials...so instead smtpd
    # sees the credential sent by smtplib's login method jako an unknown command,
    # which results w smtplib raising an auth error.  Fortunately the error
    # message contains the encoded credential, so we can partially check that it
    # was generated correctly (partially, because the 'word' jest uppercased w
    # the error message).

    def testAUTH_PLAIN(self):
        self.serv.add_feature("AUTH PLAIN")
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        spróbuj: smtp.login(sim_auth[0], sim_auth[1], initial_response_ok=Nieprawda)
        wyjąwszy smtplib.SMTPAuthenticationError jako err:
            self.assertIn(sim_auth_plain, str(err))
        smtp.close()

    def testAUTH_LOGIN(self):
        self.serv.add_feature("AUTH LOGIN")
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        spróbuj: smtp.login(sim_auth[0], sim_auth[1])
        wyjąwszy smtplib.SMTPAuthenticationError jako err:
            self.assertIn(sim_auth_login_user, str(err))
        smtp.close()

    def testAUTH_CRAM_MD5(self):
        self.serv.add_feature("AUTH CRAM-MD5")
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)

        spróbuj: smtp.login(sim_auth[0], sim_auth[1])
        wyjąwszy smtplib.SMTPAuthenticationError jako err:
            self.assertIn(sim_auth_credentials['cram-md5'], str(err))
        smtp.close()

    def testAUTH_multiple(self):
        # Test that multiple authentication methods are tried.
        self.serv.add_feature("AUTH BOGUS PLAIN LOGIN CRAM-MD5")
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        spróbuj: smtp.login(sim_auth[0], sim_auth[1])
        wyjąwszy smtplib.SMTPAuthenticationError jako err:
            self.assertIn(sim_auth_login_user, str(err))
        smtp.close()

    def test_auth_function(self):
        smtp = smtplib.SMTP(HOST, self.port,
                            local_hostname='localhost', timeout=15)
        self.serv.add_feature("AUTH CRAM-MD5")
        smtp.user, smtp.password = sim_auth[0], sim_auth[1]
        supported = {'CRAM-MD5': smtp.auth_cram_md5,
                     'PLAIN': smtp.auth_plain,
                     'LOGIN': smtp.auth_login,
                    }
        dla mechanism, method w supported.items():
            spróbuj: smtp.auth(mechanism, method, initial_response_ok=Nieprawda)
            wyjąwszy smtplib.SMTPAuthenticationError jako err:
                self.assertIn(sim_auth_credentials[mechanism.lower()].upper(),
                              str(err))
        smtp.close()

    def test_quit_resets_greeting(self):
        smtp = smtplib.SMTP(HOST, self.port,
                            local_hostname='localhost',
                            timeout=15)
        code, message = smtp.ehlo()
        self.assertEqual(code, 250)
        self.assertIn('size', smtp.esmtp_features)
        smtp.quit()
        self.assertNotIn('size', smtp.esmtp_features)
        smtp.connect(HOST, self.port)
        self.assertNotIn('size', smtp.esmtp_features)
        smtp.ehlo_or_helo_if_needed()
        self.assertIn('size', smtp.esmtp_features)
        smtp.quit()

    def test_with_statement(self):
        przy smtplib.SMTP(HOST, self.port) jako smtp:
            code, message = smtp.noop()
            self.assertEqual(code, 250)
        self.assertRaises(smtplib.SMTPServerDisconnected, smtp.send, b'foo')
        przy smtplib.SMTP(HOST, self.port) jako smtp:
            smtp.close()
        self.assertRaises(smtplib.SMTPServerDisconnected, smtp.send, b'foo')

    def test_with_statement_QUIT_failure(self):
        przy self.assertRaises(smtplib.SMTPResponseException) jako error:
            przy smtplib.SMTP(HOST, self.port) jako smtp:
                smtp.noop()
                self.serv._SMTPchannel.quit_response = '421 QUIT FAILED'
        self.assertEqual(error.exception.smtp_code, 421)
        self.assertEqual(error.exception.smtp_error, b'QUIT FAILED')

    #TODO: add tests dla correct AUTH method fallback now that the
    #test infrastructure can support it.

    # Issue 17498: make sure _rset does nie podnieś SMTPServerDisconnected exception
    def test__rest_from_mail_cmd(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        smtp.noop()
        self.serv._SMTPchannel.mail_response = '451 Requested action aborted'
        self.serv._SMTPchannel.disconnect = Prawda
        przy self.assertRaises(smtplib.SMTPSenderRefused):
            smtp.sendmail('John', 'Sally', 'test message')
        self.assertIsNic(smtp.sock)

    # Issue 5713: make sure close, nie rset, jest called jeżeli we get a 421 error
    def test_421_from_mail_cmd(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        smtp.noop()
        self.serv._SMTPchannel.mail_response = '421 closing connection'
        przy self.assertRaises(smtplib.SMTPSenderRefused):
            smtp.sendmail('John', 'Sally', 'test message')
        self.assertIsNic(smtp.sock)
        self.assertEqual(self.serv._SMTPchannel.rset_count, 0)

    def test_421_from_rcpt_cmd(self):
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        smtp.noop()
        self.serv._SMTPchannel.rcpt_response = ['250 accepted', '421 closing']
        przy self.assertRaises(smtplib.SMTPRecipientsRefused) jako r:
            smtp.sendmail('John', ['Sally', 'Frank', 'George'], 'test message')
        self.assertIsNic(smtp.sock)
        self.assertEqual(self.serv._SMTPchannel.rset_count, 0)
        self.assertDictEqual(r.exception.args[0], {'Frank': (421, b'closing')})

    def test_421_from_data_cmd(self):
        klasa MySimSMTPChannel(SimSMTPChannel):
            def found_terminator(self):
                jeżeli self.smtp_state == self.DATA:
                    self.push('421 closing')
                inaczej:
                    super().found_terminator()
        self.serv.channel_class = MySimSMTPChannel
        smtp = smtplib.SMTP(HOST, self.port, local_hostname='localhost', timeout=15)
        smtp.noop()
        przy self.assertRaises(smtplib.SMTPDataError):
            smtp.sendmail('John@foo.org', ['Sally@foo.org'], 'test message')
        self.assertIsNic(smtp.sock)
        self.assertEqual(self.serv._SMTPchannel.rcpt_count, 0)

    def test_smtputf8_NotSupportedError_if_no_server_support(self):
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        smtp.ehlo()
        self.assertPrawda(smtp.does_esmtp)
        self.assertNieprawda(smtp.has_extn('smtputf8'))
        self.assertRaises(
            smtplib.SMTPNotSupportedError,
            smtp.sendmail,
            'John', 'Sally', '', mail_options=['BODY=8BITMIME', 'SMTPUTF8'])
        self.assertRaises(
            smtplib.SMTPNotSupportedError,
            smtp.mail, 'John', options=['BODY=8BITMIME', 'SMTPUTF8'])

    def test_send_unicode_without_SMTPUTF8(self):
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        self.assertRaises(UnicodeEncodeError, smtp.sendmail, 'Alice', 'Böb', '')
        self.assertRaises(UnicodeEncodeError, smtp.mail, 'Älice')


klasa SimSMTPUTF8Server(SimSMTPServer):

    def __init__(self, *args, **kw):
        # The base SMTP server turns these on automatically, but our test
        # server jest set up to munge the EHLO response, so we need to provide
        # them jako well.  And yes, the call jest to SMTPServer nie SimSMTPServer.
        self._extra_features = ['SMTPUTF8', '8BITMIME']
        smtpd.SMTPServer.__init__(self, *args, **kw)

    def handle_accepted(self, conn, addr):
        self._SMTPchannel = self.channel_class(
            self._extra_features, self, conn, addr,
            decode_data=self._decode_data,
            enable_SMTPUTF8=self.enable_SMTPUTF8,
        )

    def process_message(self, peer, mailfrom, rcpttos, data, mail_options=Nic,
                                                             rcpt_options=Nic):
        self.last_peer = peer
        self.last_mailz = mailfrom
        self.last_rcpttos = rcpttos
        self.last_message = data
        self.last_mail_options = mail_options
        self.last_rcpt_options = rcpt_options


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SMTPUTF8SimTests(unittest.TestCase):

    maxDiff = Nic

    def setUp(self):
        self.real_getfqdn = socket.getfqdn
        socket.getfqdn = mock_socket.getfqdn
        self.serv_evt = threading.Event()
        self.client_evt = threading.Event()
        # Pick a random unused port by dalejing 0 dla the port number
        self.serv = SimSMTPUTF8Server((HOST, 0), ('nowhere', -1),
                                      decode_data=Nieprawda,
                                      enable_SMTPUTF8=Prawda)
        # Keep a note of what port was assigned
        self.port = self.serv.socket.getsockname()[1]
        serv_args = (self.serv, self.serv_evt, self.client_evt)
        self.thread = threading.Thread(target=debugging_server, args=serv_args)
        self.thread.start()

        # wait until server thread has assigned a port number
        self.serv_evt.wait()
        self.serv_evt.clear()

    def tearDown(self):
        socket.getfqdn = self.real_getfqdn
        # indicate that the client jest finished
        self.client_evt.set()
        # wait dla the server thread to terminate
        self.serv_evt.wait()
        self.thread.join()

    def test_test_server_supports_extensions(self):
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        smtp.ehlo()
        self.assertPrawda(smtp.does_esmtp)
        self.assertPrawda(smtp.has_extn('smtputf8'))

    def test_send_unicode_with_SMTPUTF8_via_sendmail(self):
        m = '¡a test message containing unicode!'.encode('utf-8')
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        smtp.sendmail('Jőhn', 'Sálly', m,
                      mail_options=['BODY=8BITMIME', 'SMTPUTF8'])
        self.assertEqual(self.serv.last_mailfrom, 'Jőhn')
        self.assertEqual(self.serv.last_rcpttos, ['Sálly'])
        self.assertEqual(self.serv.last_message, m)
        self.assertIn('BODY=8BITMIME', self.serv.last_mail_options)
        self.assertIn('SMTPUTF8', self.serv.last_mail_options)
        self.assertEqual(self.serv.last_rcpt_options, [])

    def test_send_unicode_with_SMTPUTF8_via_low_level_API(self):
        m = '¡a test message containing unicode!'.encode('utf-8')
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        smtp.ehlo()
        self.assertEqual(
            smtp.mail('Jő', options=['BODY=8BITMIME', 'SMTPUTF8']),
            (250, b'OK'))
        self.assertEqual(smtp.rcpt('János'), (250, b'OK'))
        self.assertEqual(smtp.data(m), (250, b'OK'))
        self.assertEqual(self.serv.last_mailfrom, 'Jő')
        self.assertEqual(self.serv.last_rcpttos, ['János'])
        self.assertEqual(self.serv.last_message, m)
        self.assertIn('BODY=8BITMIME', self.serv.last_mail_options)
        self.assertIn('SMTPUTF8', self.serv.last_mail_options)
        self.assertEqual(self.serv.last_rcpt_options, [])

    def test_send_message_uses_smtputf8_if_addrs_non_ascii(self):
        msg = EmailMessage()
        msg['From'] = "Páolo <főo@bar.com>"
        msg['To'] = 'Dinsdale'
        msg['Subject'] = 'Nudge nudge, wink, wink \u1F609'
        # XXX I don't know why I need two \n's here, but this jest an existing
        # bug (jeżeli it jest one) oraz nie a problem przy the new functionality.
        msg.set_content("oh là là, know what I mean, know what I mean?\n\n")
        # XXX smtpd converts received /r/n to /n, so we can't easily test that
        # we are successfully sending /r/n :(.
        expected = textwrap.dedent("""\
            From: Páolo <főo@bar.com>
            To: Dinsdale
            Subject: Nudge nudge, wink, wink \u1F609
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 8bit
            MIME-Version: 1.0

            oh là là, know what I mean, know what I mean?
            """)
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        self.assertEqual(smtp.send_message(msg), {})
        self.assertEqual(self.serv.last_mailfrom, 'főo@bar.com')
        self.assertEqual(self.serv.last_rcpttos, ['Dinsdale'])
        self.assertEqual(self.serv.last_message.decode(), expected)
        self.assertIn('BODY=8BITMIME', self.serv.last_mail_options)
        self.assertIn('SMTPUTF8', self.serv.last_mail_options)
        self.assertEqual(self.serv.last_rcpt_options, [])

    def test_send_message_error_on_non_ascii_addrs_if_no_smtputf8(self):
        msg = EmailMessage()
        msg['From'] = "Páolo <főo@bar.com>"
        msg['To'] = 'Dinsdale'
        msg['Subject'] = 'Nudge nudge, wink, wink \u1F609'
        smtp = smtplib.SMTP(
            HOST, self.port, local_hostname='localhost', timeout=3)
        self.addCleanup(smtp.close)
        self.assertRaises(smtplib.SMTPNotSupportedError,
                          smtp.send_message(msg))


EXPECTED_RESPONSE = encode_base64(b'\0psu\0doesnotexist', eol='')

klasa SimSMTPAUTHInitialResponseChannel(SimSMTPChannel):
    def smtp_AUTH(self, arg):
        # RFC 4954's AUTH command allows dla an optional initial-response.
        # Not all AUTH methods support this; some require a challenge.  AUTH
        # PLAIN does those, so test that here.  See issue #15014.
        args = arg.split()
        jeżeli args[0].lower() == 'plain':
            jeżeli len(args) == 2:
                # AUTH PLAIN <initial-response> przy the response base 64
                # encoded.  Hard code the expected response dla the test.
                jeżeli args[1] == EXPECTED_RESPONSE:
                    self.push('235 Ok')
                    zwróć
        self.push('571 Bad authentication')

klasa SimSMTPAUTHInitialResponseServer(SimSMTPServer):
    channel_class = SimSMTPAUTHInitialResponseChannel


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SMTPAUTHInitialResponseSimTests(unittest.TestCase):
    def setUp(self):
        self.real_getfqdn = socket.getfqdn
        socket.getfqdn = mock_socket.getfqdn
        self.serv_evt = threading.Event()
        self.client_evt = threading.Event()
        # Pick a random unused port by dalejing 0 dla the port number
        self.serv = SimSMTPAUTHInitialResponseServer(
            (HOST, 0), ('nowhere', -1), decode_data=Prawda)
        # Keep a note of what port was assigned
        self.port = self.serv.socket.getsockname()[1]
        serv_args = (self.serv, self.serv_evt, self.client_evt)
        self.thread = threading.Thread(target=debugging_server, args=serv_args)
        self.thread.start()

        # wait until server thread has assigned a port number
        self.serv_evt.wait()
        self.serv_evt.clear()

    def tearDown(self):
        socket.getfqdn = self.real_getfqdn
        # indicate that the client jest finished
        self.client_evt.set()
        # wait dla the server thread to terminate
        self.serv_evt.wait()
        self.thread.join()

    def testAUTH_PLAIN_initial_response_login(self):
        self.serv.add_feature('AUTH PLAIN')
        smtp = smtplib.SMTP(HOST, self.port,
                            local_hostname='localhost', timeout=15)
        smtp.login('psu', 'doesnotexist')
        smtp.close()

    def testAUTH_PLAIN_initial_response_auth(self):
        self.serv.add_feature('AUTH PLAIN')
        smtp = smtplib.SMTP(HOST, self.port,
                            local_hostname='localhost', timeout=15)
        smtp.user = 'psu'
        smtp.password = 'doesnotexist'
        code, response = smtp.auth('plain', smtp.auth_plain)
        smtp.close()
        self.assertEqual(code, 235)


@support.reap_threads
def test_main(verbose=Nic):
    support.run_unittest(
        BadHELOServerTests,
        DebuggingServerTests,
        GeneralTests,
        NonConnectingTests,
        SMTPAUTHInitialResponseSimTests,
        SMTPSimTests,
        TooLongLineTests,
        )


jeżeli __name__ == '__main__':
    test_main()
