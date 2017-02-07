zaimportuj base64
zaimportuj datetime
zaimportuj sys
zaimportuj time
zaimportuj unittest
z unittest zaimportuj mock
zaimportuj xmlrpc.client jako xmlrpclib
zaimportuj xmlrpc.server
zaimportuj http.client
zaimportuj socket
zaimportuj os
zaimportuj re
zaimportuj io
zaimportuj contextlib
z test zaimportuj support

spróbuj:
    zaimportuj gzip
wyjąwszy ImportError:
    gzip = Nic
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

alist = [{'astring': 'foo@bar.baz.spam',
          'afloat': 7283.43,
          'anint': 2**20,
          'ashortlong': 2,
          'anotherlist': ['.zyx.41'],
          'abase64': xmlrpclib.Binary(b"my dog has fleas"),
          'b64bytes': b"my dog has fleas",
          'b64bytearray': bytearray(b"my dog has fleas"),
          'boolean': Nieprawda,
          'unicode': '\u4000\u6000\u8000',
          'ukey\u4000': 'regular value',
          'datetime1': xmlrpclib.DateTime('20050210T11:41:23'),
          'datetime2': xmlrpclib.DateTime(
                        (2005, 2, 10, 11, 41, 23, 0, 1, -1)),
          'datetime3': xmlrpclib.DateTime(
                        datetime.datetime(2005, 2, 10, 11, 41, 23)),
          }]

klasa XMLRPCTestCase(unittest.TestCase):

    def test_dump_load(self):
        dump = xmlrpclib.dumps((alist,))
        load = xmlrpclib.loads(dump)
        self.assertEqual(alist, load[0][0])

    def test_dump_bare_datetime(self):
        # This checks that an unwrapped datetime.date object can be handled
        # by the marshalling code.  This can't be done via test_dump_load()
        # since przy use_builtin_types set to 1 the unmarshaller would create
        # datetime objects dla the 'datetime[123]' keys jako well
        dt = datetime.datetime(2005, 2, 10, 11, 41, 23)
        self.assertEqual(dt, xmlrpclib.DateTime('20050210T11:41:23'))
        s = xmlrpclib.dumps((dt,))

        result, m = xmlrpclib.loads(s, use_builtin_types=Prawda)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), datetime.datetime)
        self.assertIsNic(m)

        result, m = xmlrpclib.loads(s, use_builtin_types=Nieprawda)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), xmlrpclib.DateTime)
        self.assertIsNic(m)

        result, m = xmlrpclib.loads(s, use_datetime=Prawda)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), datetime.datetime)
        self.assertIsNic(m)

        result, m = xmlrpclib.loads(s, use_datetime=Nieprawda)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), xmlrpclib.DateTime)
        self.assertIsNic(m)


    def test_datetime_before_1900(self):
        # same jako before but przy a date before 1900
        dt = datetime.datetime(1,  2, 10, 11, 41, 23)
        self.assertEqual(dt, xmlrpclib.DateTime('00010210T11:41:23'))
        s = xmlrpclib.dumps((dt,))

        result, m = xmlrpclib.loads(s, use_builtin_types=Prawda)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), datetime.datetime)
        self.assertIsNic(m)

        result, m = xmlrpclib.loads(s, use_builtin_types=Nieprawda)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), xmlrpclib.DateTime)
        self.assertIsNic(m)

    def test_bug_1164912 (self):
        d = xmlrpclib.DateTime()
        ((new_d,), dummy) = xmlrpclib.loads(xmlrpclib.dumps((d,),
                                            methodresponse=Prawda))
        self.assertIsInstance(new_d.value, str)

        # Check that the output of dumps() jest still an 8-bit string
        s = xmlrpclib.dumps((new_d,), methodresponse=Prawda)
        self.assertIsInstance(s, str)

    def test_newstyle_class(self):
        klasa T(object):
            dalej
        t = T()
        t.x = 100
        t.y = "Hello"
        ((t2,), dummy) = xmlrpclib.loads(xmlrpclib.dumps((t,)))
        self.assertEqual(t2, t.__dict__)

    def test_dump_big_long(self):
        self.assertRaises(OverflowError, xmlrpclib.dumps, (2**99,))

    def test_dump_bad_dict(self):
        self.assertRaises(TypeError, xmlrpclib.dumps, ({(1,2,3): 1},))

    def test_dump_recursive_seq(self):
        l = [1,2,3]
        t = [3,4,5,l]
        l.append(t)
        self.assertRaises(TypeError, xmlrpclib.dumps, (l,))

    def test_dump_recursive_dict(self):
        d = {'1':1, '2':1}
        t = {'3':3, 'd':d}
        d['t'] = t
        self.assertRaises(TypeError, xmlrpclib.dumps, (d,))

    def test_dump_big_int(self):
        jeżeli sys.maxsize > 2**31-1:
            self.assertRaises(OverflowError, xmlrpclib.dumps,
                              (int(2**34),))

        xmlrpclib.dumps((xmlrpclib.MAXINT, xmlrpclib.MININT))
        self.assertRaises(OverflowError, xmlrpclib.dumps,
                          (xmlrpclib.MAXINT+1,))
        self.assertRaises(OverflowError, xmlrpclib.dumps,
                          (xmlrpclib.MININT-1,))

        def dummy_write(s):
            dalej

        m = xmlrpclib.Marshaller()
        m.dump_int(xmlrpclib.MAXINT, dummy_write)
        m.dump_int(xmlrpclib.MININT, dummy_write)
        self.assertRaises(OverflowError, m.dump_int,
                          xmlrpclib.MAXINT+1, dummy_write)
        self.assertRaises(OverflowError, m.dump_int,
                          xmlrpclib.MININT-1, dummy_write)

    def test_dump_double(self):
        xmlrpclib.dumps((float(2 ** 34),))
        xmlrpclib.dumps((float(xmlrpclib.MAXINT),
                         float(xmlrpclib.MININT)))
        xmlrpclib.dumps((float(xmlrpclib.MAXINT + 42),
                         float(xmlrpclib.MININT - 42)))

        def dummy_write(s):
            dalej

        m = xmlrpclib.Marshaller()
        m.dump_double(xmlrpclib.MAXINT, dummy_write)
        m.dump_double(xmlrpclib.MININT, dummy_write)
        m.dump_double(xmlrpclib.MAXINT + 42, dummy_write)
        m.dump_double(xmlrpclib.MININT - 42, dummy_write)

    def test_dump_none(self):
        value = alist + [Nic]
        arg1 = (alist + [Nic],)
        strg = xmlrpclib.dumps(arg1, allow_none=Prawda)
        self.assertEqual(value,
                          xmlrpclib.loads(strg)[0][0])
        self.assertRaises(TypeError, xmlrpclib.dumps, (arg1,))

    def test_dump_bytes(self):
        sample = b"my dog has fleas"
        self.assertEqual(sample, xmlrpclib.Binary(sample))
        dla type_ w bytes, bytearray, xmlrpclib.Binary:
            value = type_(sample)
            s = xmlrpclib.dumps((value,))

            result, m = xmlrpclib.loads(s, use_builtin_types=Prawda)
            (newvalue,) = result
            self.assertEqual(newvalue, sample)
            self.assertIs(type(newvalue), bytes)
            self.assertIsNic(m)

            result, m = xmlrpclib.loads(s, use_builtin_types=Nieprawda)
            (newvalue,) = result
            self.assertEqual(newvalue, sample)
            self.assertIs(type(newvalue), xmlrpclib.Binary)
            self.assertIsNic(m)

    def test_get_host_info(self):
        # see bug #3613, this podnieśd a TypeError
        transp = xmlrpc.client.Transport()
        self.assertEqual(transp.get_host_info("user@host.tld"),
                          ('host.tld',
                           [('Authorization', 'Basic dXNlcg==')], {}))

    def test_ssl_presence(self):
        spróbuj:
            zaimportuj ssl
        wyjąwszy ImportError:
            has_ssl = Nieprawda
        inaczej:
            has_ssl = Prawda
        spróbuj:
            xmlrpc.client.ServerProxy('https://localhost:9999').bad_function()
        wyjąwszy NotImplementedError:
            self.assertNieprawda(has_ssl, "xmlrpc client's error przy SSL support")
        wyjąwszy OSError:
            self.assertPrawda(has_ssl)

klasa HelperTestCase(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(xmlrpclib.escape("a&b"), "a&amp;b")
        self.assertEqual(xmlrpclib.escape("a<b"), "a&lt;b")
        self.assertEqual(xmlrpclib.escape("a>b"), "a&gt;b")

klasa FaultTestCase(unittest.TestCase):
    def test_repr(self):
        f = xmlrpclib.Fault(42, 'Test Fault')
        self.assertEqual(repr(f), "<Fault 42: 'Test Fault'>")
        self.assertEqual(repr(f), str(f))

    def test_dump_fault(self):
        f = xmlrpclib.Fault(42, 'Test Fault')
        s = xmlrpclib.dumps((f,))
        (newf,), m = xmlrpclib.loads(s)
        self.assertEqual(newf, {'faultCode': 42, 'faultString': 'Test Fault'})
        self.assertEqual(m, Nic)

        s = xmlrpclib.Marshaller().dumps(f)
        self.assertRaises(xmlrpclib.Fault, xmlrpclib.loads, s)

    def test_dotted_attribute(self):
        # this will podnieś AttributeError because code don't want us to use
        # private methods
        self.assertRaises(AttributeError,
                          xmlrpc.server.resolve_dotted_attribute, str, '__add')
        self.assertPrawda(xmlrpc.server.resolve_dotted_attribute(str, 'title'))

klasa DateTimeTestCase(unittest.TestCase):
    def test_default(self):
        przy mock.patch('time.localtime') jako localtime_mock:
            time_struct = time.struct_time(
                [2013, 7, 15, 0, 24, 49, 0, 196, 0])
            localtime_mock.return_value = time_struct
            localtime = time.localtime()
            t = xmlrpclib.DateTime()
            self.assertEqual(str(t),
                             time.strftime("%Y%m%dT%H:%M:%S", localtime))

    def test_time(self):
        d = 1181399930.036952
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t),
                         time.strftime("%Y%m%dT%H:%M:%S", time.localtime(d)))

    def test_time_tuple(self):
        d = (2007,6,9,10,38,50,5,160,0)
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t), '20070609T10:38:50')

    def test_time_struct(self):
        d = time.localtime(1181399930.036952)
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t), time.strftime("%Y%m%dT%H:%M:%S", d))

    def test_datetime_datetime(self):
        d = datetime.datetime(2007,1,2,3,4,5)
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t), '20070102T03:04:05')

    def test_repr(self):
        d = datetime.datetime(2007,1,2,3,4,5)
        t = xmlrpclib.DateTime(d)
        val ="<DateTime '20070102T03:04:05' at %#x>" % id(t)
        self.assertEqual(repr(t), val)

    def test_decode(self):
        d = ' 20070908T07:11:13  '
        t1 = xmlrpclib.DateTime()
        t1.decode(d)
        tref = xmlrpclib.DateTime(datetime.datetime(2007,9,8,7,11,13))
        self.assertEqual(t1, tref)

        t2 = xmlrpclib._datetime(d)
        self.assertEqual(t2, tref)

    def test_comparison(self):
        now = datetime.datetime.now()
        dtime = xmlrpclib.DateTime(now.timetuple())

        # datetime vs. DateTime
        self.assertPrawda(dtime == now)
        self.assertPrawda(now == dtime)
        then = now + datetime.timedelta(seconds=4)
        self.assertPrawda(then >= dtime)
        self.assertPrawda(dtime < then)

        # str vs. DateTime
        dstr = now.strftime("%Y%m%dT%H:%M:%S")
        self.assertPrawda(dtime == dstr)
        self.assertPrawda(dstr == dtime)
        dtime_then = xmlrpclib.DateTime(then.timetuple())
        self.assertPrawda(dtime_then >= dstr)
        self.assertPrawda(dstr < dtime_then)

        # some other types
        dbytes = dstr.encode('ascii')
        dtuple = now.timetuple()
        przy self.assertRaises(TypeError):
            dtime == 1970
        przy self.assertRaises(TypeError):
            dtime != dbytes
        przy self.assertRaises(TypeError):
            dtime == bytearray(dbytes)
        przy self.assertRaises(TypeError):
            dtime != dtuple
        przy self.assertRaises(TypeError):
            dtime < float(1970)
        przy self.assertRaises(TypeError):
            dtime > dbytes
        przy self.assertRaises(TypeError):
            dtime <= bytearray(dbytes)
        przy self.assertRaises(TypeError):
            dtime >= dtuple

klasa BinaryTestCase(unittest.TestCase):

    # XXX What should str(Binary(b"\xff")) return?  I'm chosing "\xff"
    # dla now (i.e. interpreting the binary data jako Latin-1-encoded
    # text).  But this feels very unsatisfactory.  Perhaps we should
    # only define repr(), oraz zwróć r"Binary(b'\xff')" instead?

    def test_default(self):
        t = xmlrpclib.Binary()
        self.assertEqual(str(t), '')

    def test_string(self):
        d = b'\x01\x02\x03abc123\xff\xfe'
        t = xmlrpclib.Binary(d)
        self.assertEqual(str(t), str(d, "latin-1"))

    def test_decode(self):
        d = b'\x01\x02\x03abc123\xff\xfe'
        de = base64.encodebytes(d)
        t1 = xmlrpclib.Binary()
        t1.decode(de)
        self.assertEqual(str(t1), str(d, "latin-1"))

        t2 = xmlrpclib._binary(de)
        self.assertEqual(str(t2), str(d, "latin-1"))


ADDR = PORT = URL = Nic

# The evt jest set twice.  First when the server jest ready to serve.
# Second when the server has been shutdown.  The user must clear
# the event after it has been set the first time to catch the second set.
def http_server(evt, numrequests, requestHandler=Nic):
    klasa TestInstanceClass:
        def div(self, x, y):
            zwróć x // y

        def _methodHelp(self, name):
            jeżeli name == 'div':
                zwróć 'This jest the div function'

        klasa Fixture:
            @staticmethod
            def getData():
                zwróć '42'

    def my_function():
        '''This jest my function'''
        zwróć Prawda

    klasa MyXMLRPCServer(xmlrpc.server.SimpleXMLRPCServer):
        def get_request(self):
            # Ensure the socket jest always non-blocking.  On Linux, socket
            # attributes are nie inherited like they are on *BSD oraz Windows.
            s, port = self.socket.accept()
            s.setblocking(Prawda)
            zwróć s, port

    jeżeli nie requestHandler:
        requestHandler = xmlrpc.server.SimpleXMLRPCRequestHandler
    serv = MyXMLRPCServer(("localhost", 0), requestHandler,
                          logRequests=Nieprawda, bind_and_activate=Nieprawda)
    spróbuj:
        serv.server_bind()
        global ADDR, PORT, URL
        ADDR, PORT = serv.socket.getsockname()
        #connect to IP address directly.  This avoids socket.create_connection()
        #trying to connect to "localhost" using all address families, which
        #causes slowdown e.g. on vista which supports AF_INET6.  The server listens
        #on AF_INET only.
        URL = "http://%s:%d"%(ADDR, PORT)
        serv.server_activate()
        serv.register_introspection_functions()
        serv.register_multicall_functions()
        serv.register_function(pow)
        serv.register_function(lambda x,y: x+y, 'add')
        serv.register_function(my_function)
        testInstance = TestInstanceClass()
        serv.register_instance(testInstance, allow_dotted_names=Prawda)
        evt.set()

        # handle up to 'numrequests' requests
        dopóki numrequests > 0:
            serv.handle_request()
            numrequests -= 1

    wyjąwszy socket.timeout:
        dalej
    w_końcu:
        serv.socket.close()
        PORT = Nic
        evt.set()

def http_multi_server(evt, numrequests, requestHandler=Nic):
    klasa TestInstanceClass:
        def div(self, x, y):
            zwróć x // y

        def _methodHelp(self, name):
            jeżeli name == 'div':
                zwróć 'This jest the div function'

    def my_function():
        '''This jest my function'''
        zwróć Prawda

    klasa MyXMLRPCServer(xmlrpc.server.MultiPathXMLRPCServer):
        def get_request(self):
            # Ensure the socket jest always non-blocking.  On Linux, socket
            # attributes are nie inherited like they are on *BSD oraz Windows.
            s, port = self.socket.accept()
            s.setblocking(Prawda)
            zwróć s, port

    jeżeli nie requestHandler:
        requestHandler = xmlrpc.server.SimpleXMLRPCRequestHandler
    klasa MyRequestHandler(requestHandler):
        rpc_paths = []

    klasa BrokenDispatcher:
        def _marshaled_dispatch(self, data, dispatch_method=Nic, path=Nic):
            podnieś RuntimeError("broken dispatcher")

    serv = MyXMLRPCServer(("localhost", 0), MyRequestHandler,
                          logRequests=Nieprawda, bind_and_activate=Nieprawda)
    serv.socket.settimeout(3)
    serv.server_bind()
    spróbuj:
        global ADDR, PORT, URL
        ADDR, PORT = serv.socket.getsockname()
        #connect to IP address directly.  This avoids socket.create_connection()
        #trying to connect to "localhost" using all address families, which
        #causes slowdown e.g. on vista which supports AF_INET6.  The server listens
        #on AF_INET only.
        URL = "http://%s:%d"%(ADDR, PORT)
        serv.server_activate()
        paths = ["/foo", "/foo/bar"]
        dla path w paths:
            d = serv.add_dispatcher(path, xmlrpc.server.SimpleXMLRPCDispatcher())
            d.register_introspection_functions()
            d.register_multicall_functions()
        serv.get_dispatcher(paths[0]).register_function(pow)
        serv.get_dispatcher(paths[1]).register_function(lambda x,y: x+y, 'add')
        serv.add_dispatcher("/is/broken", BrokenDispatcher())
        evt.set()

        # handle up to 'numrequests' requests
        dopóki numrequests > 0:
            serv.handle_request()
            numrequests -= 1

    wyjąwszy socket.timeout:
        dalej
    w_końcu:
        serv.socket.close()
        PORT = Nic
        evt.set()

# This function prevents errors like:
#    <ProtocolError dla localhost:57527/RPC2: 500 Internal Server Error>
def is_unavailable_exception(e):
    '''Returns Prawda jeżeli the given ProtocolError jest the product of a server-side
       exception caused by the 'temporarily unavailable' response sometimes
       given by operations on non-blocking sockets.'''

    # sometimes we get a -1 error code and/or empty headers
    spróbuj:
        jeżeli e.errcode == -1 albo e.headers jest Nic:
            zwróć Prawda
        exc_mess = e.headers.get('X-exception')
    wyjąwszy AttributeError:
        # Ignore OSErrors here.
        exc_mess = str(e)

    jeżeli exc_mess oraz 'temporarily unavailable' w exc_mess.lower():
        zwróć Prawda

def make_request_and_skipIf(condition, reason):
    # If we skip the test, we have to make a request because
    # the server created w setUp blocks expecting one to come in.
    jeżeli nie condition:
        zwróć lambda func: func
    def decorator(func):
        def make_request_and_skip(self):
            spróbuj:
                xmlrpclib.ServerProxy(URL).my_function()
            wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
                jeżeli nie is_unavailable_exception(e):
                    podnieś
            podnieś unittest.SkipTest(reason)
        zwróć make_request_and_skip
    zwróć decorator

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa BaseServerTestCase(unittest.TestCase):
    requestHandler = Nic
    request_count = 1
    threadFunc = staticmethod(http_server)

    def setUp(self):
        # enable traceback reporting
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Prawda

        self.evt = threading.Event()
        # start server thread to handle requests
        serv_args = (self.evt, self.request_count, self.requestHandler)
        threading.Thread(target=self.threadFunc, args=serv_args).start()

        # wait dla the server to be ready
        self.evt.wait()
        self.evt.clear()

    def tearDown(self):
        # wait on the server thread to terminate
        self.evt.wait()

        # disable traceback reporting
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Nieprawda

klasa SimpleServerTestCase(BaseServerTestCase):
    def test_simple1(self):
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.pow(6,8), 6**8)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    def test_nonascii(self):
        start_string = 'P\N{LATIN SMALL LETTER Y WITH CIRCUMFLEX}t'
        end_string = 'h\N{LATIN SMALL LETTER O WITH HORN}n'
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.add(start_string, end_string),
                             start_string + end_string)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    # [ch] The test 404 jest causing lots of false alarms.
    def XXXtest_404(self):
        # send POST przy http.client, it should zwróć 404 header oraz
        # 'Not Found' message.
        conn = httplib.client.HTTPConnection(ADDR, PORT)
        conn.request('POST', '/this-is-not-valid')
        response = conn.getresponse()
        conn.close()

        self.assertEqual(response.status, 404)
        self.assertEqual(response.reason, 'Not Found')

    def test_introspection1(self):
        expected_methods = set(['pow', 'div', 'my_function', 'add',
                                'system.listMethods', 'system.methodHelp',
                                'system.methodSignature', 'system.multicall',
                                'Fixture'])
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            meth = p.system.listMethods()
            self.assertEqual(set(meth), expected_methods)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))


    def test_introspection2(self):
        spróbuj:
            # test _methodHelp()
            p = xmlrpclib.ServerProxy(URL)
            divhelp = p.system.methodHelp('div')
            self.assertEqual(divhelp, 'This jest the div function')
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    @make_request_and_skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_introspection3(self):
        spróbuj:
            # test native doc
            p = xmlrpclib.ServerProxy(URL)
            myfunction = p.system.methodHelp('my_function')
            self.assertEqual(myfunction, 'This jest my function')
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    def test_introspection4(self):
        # the SimpleXMLRPCServer doesn't support signatures, but
        # at least check that we can try making the call
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            divsig = p.system.methodSignature('div')
            self.assertEqual(divsig, 'signatures nie supported')
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    def test_multicall(self):
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            multicall = xmlrpclib.MultiCall(p)
            multicall.add(2,3)
            multicall.pow(6,8)
            multicall.div(127,42)
            add_result, pow_result, div_result = multicall()
            self.assertEqual(add_result, 2+3)
            self.assertEqual(pow_result, 6**8)
            self.assertEqual(div_result, 127//42)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    def test_non_existing_multicall(self):
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            multicall = xmlrpclib.MultiCall(p)
            multicall.this_is_not_exists()
            result = multicall()

            # result.results contains;
            # [{'faultCode': 1, 'faultString': '<class \'exceptions.Exception\'>:'
            #   'method "this_is_not_exists" jest nie supported'>}]

            self.assertEqual(result.results[0]['faultCode'], 1)
            self.assertEqual(result.results[0]['faultString'],
                '<class \'Exception\'>:method "this_is_not_exists" '
                'is nie supported')
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    def test_dotted_attribute(self):
        # Raises an AttributeError because private methods are nie allowed.
        self.assertRaises(AttributeError,
                          xmlrpc.server.resolve_dotted_attribute, str, '__add')

        self.assertPrawda(xmlrpc.server.resolve_dotted_attribute(str, 'title'))
        # Get the test to run faster by sending a request przy test_simple1.
        # This avoids waiting dla the socket timeout.
        self.test_simple1()

    def test_allow_dotted_names_true(self):
        # XXX also need allow_dotted_names_false test.
        server = xmlrpclib.ServerProxy("http://%s:%d/RPC2" % (ADDR, PORT))
        data = server.Fixture.getData()
        self.assertEqual(data, '42')

    def test_unicode_host(self):
        server = xmlrpclib.ServerProxy("http://%s:%d/RPC2" % (ADDR, PORT))
        self.assertEqual(server.add("a", "\xe9"), "a\xe9")

    def test_partial_post(self):
        # Check that a partial POST doesn't make the server loop: issue #14001.
        conn = http.client.HTTPConnection(ADDR, PORT)
        conn.request('POST', '/RPC2 HTTP/1.0\r\nContent-Length: 100\r\n\r\nbye')
        conn.close()

    def test_context_manager(self):
        przy xmlrpclib.ServerProxy(URL) jako server:
            server.add(2, 3)
            self.assertNotEqual(server('transport')._connection,
                                (Nic, Nic))
        self.assertEqual(server('transport')._connection,
                         (Nic, Nic))

    def test_context_manager_method_error(self):
        spróbuj:
            przy xmlrpclib.ServerProxy(URL) jako server:
                server.add(2, "a")
        wyjąwszy xmlrpclib.Fault:
            dalej
        self.assertEqual(server('transport')._connection,
                         (Nic, Nic))


klasa MultiPathServerTestCase(BaseServerTestCase):
    threadFunc = staticmethod(http_multi_server)
    request_count = 2
    def test_path1(self):
        p = xmlrpclib.ServerProxy(URL+"/foo")
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertRaises(xmlrpclib.Fault, p.add, 6, 8)

    def test_path2(self):
        p = xmlrpclib.ServerProxy(URL+"/foo/bar")
        self.assertEqual(p.add(6,8), 6+8)
        self.assertRaises(xmlrpclib.Fault, p.pow, 6, 8)

    def test_path3(self):
        p = xmlrpclib.ServerProxy(URL+"/is/broken")
        self.assertRaises(xmlrpclib.Fault, p.add, 6, 8)

#A test case that verifies that a server using the HTTP/1.1 keep-alive mechanism
#does indeed serve subsequent requests on the same connection
klasa BaseKeepaliveServerTestCase(BaseServerTestCase):
    #a request handler that supports keep-alive oraz logs requests into a
    #class variable
    klasa RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
        parentClass = xmlrpc.server.SimpleXMLRPCRequestHandler
        protocol_version = 'HTTP/1.1'
        myRequests = []
        def handle(self):
            self.myRequests.append([])
            self.reqidx = len(self.myRequests)-1
            zwróć self.parentClass.handle(self)
        def handle_one_request(self):
            result = self.parentClass.handle_one_request(self)
            self.myRequests[self.reqidx].append(self.raw_requestline)
            zwróć result

    requestHandler = RequestHandler
    def setUp(self):
        #clear request log
        self.RequestHandler.myRequests = []
        zwróć BaseServerTestCase.setUp(self)

#A test case that verifies that a server using the HTTP/1.1 keep-alive mechanism
#does indeed serve subsequent requests on the same connection
klasa KeepaliveServerTestCase1(BaseKeepaliveServerTestCase):
    def test_two(self):
        p = xmlrpclib.ServerProxy(URL)
        #do three requests.
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()

        #they should have all been handled by a single request handler
        self.assertEqual(len(self.RequestHandler.myRequests), 1)

        #check that we did at least two (the third may be pending append
        #due to thread scheduling)
        self.assertGreaterEqual(len(self.RequestHandler.myRequests[-1]), 2)


#test special attribute access on the serverproxy, through the __call__
#function.
klasa KeepaliveServerTestCase2(BaseKeepaliveServerTestCase):
    #ask dla two keepalive requests to be handled.
    request_count=2

    def test_close(self):
        p = xmlrpclib.ServerProxy(URL)
        #do some requests przy close.
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")() #this should trigger a new keep-alive request
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()

        #they should have all been two request handlers, each having logged at least
        #two complete requests
        self.assertEqual(len(self.RequestHandler.myRequests), 2)
        self.assertGreaterEqual(len(self.RequestHandler.myRequests[-1]), 2)
        self.assertGreaterEqual(len(self.RequestHandler.myRequests[-2]), 2)


    def test_transport(self):
        p = xmlrpclib.ServerProxy(URL)
        #do some requests przy close.
        self.assertEqual(p.pow(6,8), 6**8)
        p("transport").close() #same jako above, really.
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()
        self.assertEqual(len(self.RequestHandler.myRequests), 2)

#A test case that verifies that gzip encoding works w both directions
#(dla a request oraz the response)
@unittest.skipIf(gzip jest Nic, 'requires gzip')
klasa GzipServerTestCase(BaseServerTestCase):
    #a request handler that supports keep-alive oraz logs requests into a
    #class variable
    klasa RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
        parentClass = xmlrpc.server.SimpleXMLRPCRequestHandler
        protocol_version = 'HTTP/1.1'

        def do_POST(self):
            #store content of last request w class
            self.__class__.content_length = int(self.headers["content-length"])
            zwróć self.parentClass.do_POST(self)
    requestHandler = RequestHandler

    klasa Transport(xmlrpclib.Transport):
        #custom transport, stores the response length dla our perusal
        fake_gzip = Nieprawda
        def parse_response(self, response):
            self.response_length=int(response.getheader("content-length", 0))
            zwróć xmlrpclib.Transport.parse_response(self, response)

        def send_content(self, connection, body):
            jeżeli self.fake_gzip:
                #add a lone gzip header to induce decode error remotely
                connection.putheader("Content-Encoding", "gzip")
            zwróć xmlrpclib.Transport.send_content(self, connection, body)

    def setUp(self):
        BaseServerTestCase.setUp(self)

    def test_gzip_request(self):
        t = self.Transport()
        t.encode_threshold = Nic
        p = xmlrpclib.ServerProxy(URL, transport=t)
        self.assertEqual(p.pow(6,8), 6**8)
        a = self.RequestHandler.content_length
        t.encode_threshold = 0 #turn on request encoding
        self.assertEqual(p.pow(6,8), 6**8)
        b = self.RequestHandler.content_length
        self.assertPrawda(a>b)
        p("close")()

    def test_bad_gzip_request(self):
        t = self.Transport()
        t.encode_threshold = Nic
        t.fake_gzip = Prawda
        p = xmlrpclib.ServerProxy(URL, transport=t)
        cm = self.assertRaisesRegex(xmlrpclib.ProtocolError,
                                    re.compile(r"\b400\b"))
        przy cm:
            p.pow(6, 8)
        p("close")()

    def test_gzip_response(self):
        t = self.Transport()
        p = xmlrpclib.ServerProxy(URL, transport=t)
        old = self.requestHandler.encode_threshold
        self.requestHandler.encode_threshold = Nic #no encoding
        self.assertEqual(p.pow(6,8), 6**8)
        a = t.response_length
        self.requestHandler.encode_threshold = 0 #always encode
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()
        b = t.response_length
        self.requestHandler.encode_threshold = old
        self.assertPrawda(a>b)


@unittest.skipIf(gzip jest Nic, 'requires gzip')
klasa GzipUtilTestCase(unittest.TestCase):

    def test_gzip_decode_limit(self):
        max_gzip_decode = 20 * 1024 * 1024
        data = b'\0' * max_gzip_decode
        encoded = xmlrpclib.gzip_encode(data)
        decoded = xmlrpclib.gzip_decode(encoded)
        self.assertEqual(len(decoded), max_gzip_decode)

        data = b'\0' * (max_gzip_decode + 1)
        encoded = xmlrpclib.gzip_encode(data)

        przy self.assertRaisesRegex(ValueError,
                                    "max gzipped payload length exceeded"):
            xmlrpclib.gzip_decode(encoded)

        xmlrpclib.gzip_decode(encoded, max_decode=-1)


#Test special attributes of the ServerProxy object
klasa ServerProxyTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        jeżeli threading:
            self.url = URL
        inaczej:
            # Without threading, http_server() oraz http_multi_server() will nie
            # be executed oraz URL jest still equal to Nic. 'http://' jest a just
            # enough to choose the scheme (HTTP)
            self.url = 'http://'

    def test_close(self):
        p = xmlrpclib.ServerProxy(self.url)
        self.assertEqual(p('close')(), Nic)

    def test_transport(self):
        t = xmlrpclib.Transport()
        p = xmlrpclib.ServerProxy(self.url, transport=t)
        self.assertEqual(p('transport'), t)


# This jest a contrived way to make a failure occur on the server side
# w order to test the _send_traceback_header flag on the server
klasa FailingMessageClass(http.client.HTTPMessage):
    def get(self, key, failobj=Nic):
        key = key.lower()
        jeżeli key == 'content-length':
            zwróć 'I am broken'
        zwróć super().get(key, failobj)


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa FailingServerTestCase(unittest.TestCase):
    def setUp(self):
        self.evt = threading.Event()
        # start server thread to handle requests
        serv_args = (self.evt, 1)
        threading.Thread(target=http_server, args=serv_args).start()

        # wait dla the server to be ready
        self.evt.wait()
        self.evt.clear()

    def tearDown(self):
        # wait on the server thread to terminate
        self.evt.wait()
        # reset flag
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Nieprawda
        # reset message class
        default_class = http.client.HTTPMessage
        xmlrpc.server.SimpleXMLRPCRequestHandler.MessageClass = default_class

    def test_basic(self):
        # check that flag jest false by default
        flagval = xmlrpc.server.SimpleXMLRPCServer._send_traceback_header
        self.assertEqual(flagval, Nieprawda)

        # enable traceback reporting
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Prawda

        # test a call that shouldn't fail just jako a smoke test
        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.pow(6,8), 6**8)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e):
                # protocol error; provide additional information w test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    def test_fail_no_info(self):
        # use the broken message class
        xmlrpc.server.SimpleXMLRPCRequestHandler.MessageClass = FailingMessageClass

        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            p.pow(6,8)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e) oraz hasattr(e, "headers"):
                # The two server-side error headers shouldn't be sent back w this case
                self.assertPrawda(e.headers.get("X-exception") jest Nic)
                self.assertPrawda(e.headers.get("X-traceback") jest Nic)
        inaczej:
            self.fail('ProtocolError nie podnieśd')

    def test_fail_with_info(self):
        # use the broken message class
        xmlrpc.server.SimpleXMLRPCRequestHandler.MessageClass = FailingMessageClass

        # Check that errors w the server send back exception/traceback
        # info when flag jest set
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Prawda

        spróbuj:
            p = xmlrpclib.ServerProxy(URL)
            p.pow(6,8)
        wyjąwszy (xmlrpclib.ProtocolError, OSError) jako e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            jeżeli nie is_unavailable_exception(e) oraz hasattr(e, "headers"):
                # We should get error info w the response
                expected_err = "invalid literal dla int() przy base 10: 'I am broken'"
                self.assertEqual(e.headers.get("X-exception"), expected_err)
                self.assertPrawda(e.headers.get("X-traceback") jest nie Nic)
        inaczej:
            self.fail('ProtocolError nie podnieśd')


@contextlib.contextmanager
def captured_stdout(encoding='utf-8'):
    """A variation on support.captured_stdout() which gives a text stream
    having a `buffer` attribute.
    """
    zaimportuj io
    orig_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding=encoding)
    spróbuj:
        uzyskaj sys.stdout
    w_końcu:
        sys.stdout = orig_stdout


klasa CGIHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.cgi = xmlrpc.server.CGIXMLRPCRequestHandler()

    def tearDown(self):
        self.cgi = Nic

    def test_cgi_get(self):
        przy support.EnvironmentVarGuard() jako env:
            env['REQUEST_METHOD'] = 'GET'
            # jeżeli the method jest GET oraz no request_text jest given, it runs handle_get
            # get sysout output
            przy captured_stdout(encoding=self.cgi.encoding) jako data_out:
                self.cgi.handle_request()

            # parse Status header
            data_out.seek(0)
            handle = data_out.read()
            status = handle.split()[1]
            message = ' '.join(handle.split()[2:4])

            self.assertEqual(status, '400')
            self.assertEqual(message, 'Bad Request')


    def test_cgi_xmlrpc_response(self):
        data = """<?xml version='1.0'?>
        <methodCall>
            <methodName>test_method</methodName>
            <params>
                <param>
                    <value><string>foo</string></value>
                </param>
                <param>
                    <value><string>bar</string></value>
                </param>
            </params>
        </methodCall>
        """

        przy support.EnvironmentVarGuard() jako env, \
             captured_stdout(encoding=self.cgi.encoding) jako data_out, \
             support.captured_stdin() jako data_in:
            data_in.write(data)
            data_in.seek(0)
            env['CONTENT_LENGTH'] = str(len(data))
            self.cgi.handle_request()
        data_out.seek(0)

        # will respond exception, jeżeli so, our goal jest achieved ;)
        handle = data_out.read()

        # start przy 44th char so jako nie to get http header, we just
        # need only xml
        self.assertRaises(xmlrpclib.Fault, xmlrpclib.loads, handle[44:])

        # Also test the content-length returned  by handle_request
        # Using the same test method inorder to avoid all the datapassing
        # boilerplate code.
        # Test dla bug: http://bugs.python.org/issue5040

        content = handle[handle.find("<?xml"):]

        self.assertEqual(
            int(re.search('Content-Length: (\d+)', handle).group(1)),
            len(content))


klasa UseBuiltinTypesTestCase(unittest.TestCase):

    def test_use_builtin_types(self):
        # SimpleXMLRPCDispatcher.__init__ accepts use_builtin_types, which
        # makes all dispatch of binary data jako bytes instances, oraz all
        # dispatch of datetime argument jako datetime.datetime instances.
        self.log = []
        expected_bytes = b"my dog has fleas"
        expected_date = datetime.datetime(2008, 5, 26, 18, 25, 12)
        marshaled = xmlrpclib.dumps((expected_bytes, expected_date), 'foobar')
        def foobar(*args):
            self.log.extend(args)
        handler = xmlrpc.server.SimpleXMLRPCDispatcher(
            allow_none=Prawda, encoding=Nic, use_builtin_types=Prawda)
        handler.register_function(foobar)
        handler._marshaled_dispatch(marshaled)
        self.assertEqual(len(self.log), 2)
        mybytes, mydate = self.log
        self.assertEqual(self.log, [expected_bytes, expected_date])
        self.assertIs(type(mydate), datetime.datetime)
        self.assertIs(type(mybytes), bytes)

    def test_cgihandler_has_use_builtin_types_flag(self):
        handler = xmlrpc.server.CGIXMLRPCRequestHandler(use_builtin_types=Prawda)
        self.assertPrawda(handler.use_builtin_types)

    def test_xmlrpcserver_has_use_builtin_types_flag(self):
        server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 0),
            use_builtin_types=Prawda)
        server.server_close()
        self.assertPrawda(server.use_builtin_types)


@support.reap_threads
def test_main():
    support.run_unittest(XMLRPCTestCase, HelperTestCase, DateTimeTestCase,
            BinaryTestCase, FaultTestCase, UseBuiltinTypesTestCase,
            SimpleServerTestCase, KeepaliveServerTestCase1,
            KeepaliveServerTestCase2, GzipServerTestCase, GzipUtilTestCase,
            MultiPathServerTestCase, ServerProxyTestCase, FailingServerTestCase,
            CGIHandlerTestCase)


jeżeli __name__ == "__main__":
    test_main()
