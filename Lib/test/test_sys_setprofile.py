zaimportuj gc
zaimportuj pprint
zaimportuj sys
zaimportuj unittest


klasa TestGetProfile(unittest.TestCase):
    def setUp(self):
        sys.setprofile(Nic)

    def tearDown(self):
        sys.setprofile(Nic)

    def test_empty(self):
        self.assertIsNic(sys.getprofile())

    def test_setget(self):
        def fn(*args):
            dalej

        sys.setprofile(fn)
        self.assertIs(sys.getprofile(), fn)

klasa HookWatcher:
    def __init__(self):
        self.frames = []
        self.events = []

    def callback(self, frame, event, arg):
        jeżeli (event == "call"
            albo event == "return"
            albo event == "exception"):
            self.add_event(event, frame)

    def add_event(self, event, frame=Nic):
        """Add an event to the log."""
        jeżeli frame jest Nic:
            frame = sys._getframe(1)

        spróbuj:
            frameno = self.frames.index(frame)
        wyjąwszy ValueError:
            frameno = len(self.frames)
            self.frames.append(frame)

        self.events.append((frameno, event, ident(frame)))

    def get_events(self):
        """Remove calls to add_event()."""
        disallowed = [ident(self.add_event.__func__), ident(ident)]
        self.frames = Nic

        zwróć [item dla item w self.events jeżeli item[2] nie w disallowed]


klasa ProfileSimulator(HookWatcher):
    def __init__(self, testcase):
        self.testcase = testcase
        self.stack = []
        HookWatcher.__init__(self)

    def callback(self, frame, event, arg):
        # Callback registered przy sys.setprofile()/sys.settrace()
        self.dispatch[event](self, frame)

    def trace_call(self, frame):
        self.add_event('call', frame)
        self.stack.append(frame)

    def trace_return(self, frame):
        self.add_event('return', frame)
        self.stack.pop()

    def trace_exception(self, frame):
        self.testcase.fail(
            "the profiler should never receive exception events")

    def trace_pass(self, frame):
        dalej

    dispatch = {
        'call': trace_call,
        'exception': trace_exception,
        'return': trace_return,
        'c_call': trace_pass,
        'c_return': trace_pass,
        'c_exception': trace_pass,
        }


klasa TestCaseBase(unittest.TestCase):
    def check_events(self, callable, expected):
        events = capture_events(callable, self.new_watcher())
        jeżeli events != expected:
            self.fail("Expected events:\n%s\nReceived events:\n%s"
                      % (pprint.pformat(expected), pprint.pformat(events)))


klasa ProfileHookTestCase(TestCaseBase):
    def new_watcher(self):
        zwróć HookWatcher()

    def test_simple(self):
        def f(p):
            dalej
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_exception(self):
        def f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_caught_exception(self):
        def f(p):
            spróbuj: 1/0
            wyjąwszy: dalej
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_caught_nested_exception(self):
        def f(p):
            spróbuj: 1/0
            wyjąwszy: dalej
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_nested_exception(self):
        def f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              # This isn't what I expected:
                              # (0, 'exception', protect_ident),
                              # I expected this again:
                              (1, 'return', f_ident),
                              ])

    def test_exception_in_except_clause(self):
        def f(p):
            1/0
        def g(p):
            spróbuj:
                f(p)
            wyjąwszy:
                spróbuj: f(p)
                wyjąwszy: dalej
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (3, 'call', f_ident),
                              (3, 'return', f_ident),
                              (1, 'return', g_ident),
                              ])

    def test_exception_propogation(self):
        def f(p):
            1/0
        def g(p):
            spróbuj: f(p)
            w_końcu: p.add_event("falling through")
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (1, 'falling through', g_ident),
                              (1, 'return', g_ident),
                              ])

    def test_raise_twice(self):
        def f(p):
            spróbuj: 1/0
            wyjąwszy: 1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_raise_reraise(self):
        def f(p):
            spróbuj: 1/0
            wyjąwszy: podnieś
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_raise(self):
        def f(p):
            podnieś Exception()
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_distant_exception(self):
        def f():
            1/0
        def g():
            f()
        def h():
            g()
        def i():
            h()
        def j(p):
            i()
        f_ident = ident(f)
        g_ident = ident(g)
        h_ident = ident(h)
        i_ident = ident(i)
        j_ident = ident(j)
        self.check_events(j, [(1, 'call', j_ident),
                              (2, 'call', i_ident),
                              (3, 'call', h_ident),
                              (4, 'call', g_ident),
                              (5, 'call', f_ident),
                              (5, 'return', f_ident),
                              (4, 'return', g_ident),
                              (3, 'return', h_ident),
                              (2, 'return', i_ident),
                              (1, 'return', j_ident),
                              ])

    def test_generator(self):
        def f():
            dla i w range(2):
                uzyskaj i
        def g(p):
            dla i w f():
                dalej
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              # call the iterator twice to generate values
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              # once more; returns end-of-iteration with
                              # actually raising an exception
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (1, 'return', g_ident),
                              ])

    def test_stop_iteration(self):
        def f():
            dla i w range(2):
                uzyskaj i
        def g(p):
            dla i w f():
                dalej
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              # call the iterator twice to generate values
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              # once more to hit the podnieś:
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (1, 'return', g_ident),
                              ])


klasa ProfileSimulatorTestCase(TestCaseBase):
    def new_watcher(self):
        zwróć ProfileSimulator(self)

    def test_simple(self):
        def f(p):
            dalej
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_basic_exception(self):
        def f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_caught_exception(self):
        def f(p):
            spróbuj: 1/0
            wyjąwszy: dalej
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    def test_distant_exception(self):
        def f():
            1/0
        def g():
            f()
        def h():
            g()
        def i():
            h()
        def j(p):
            i()
        f_ident = ident(f)
        g_ident = ident(g)
        h_ident = ident(h)
        i_ident = ident(i)
        j_ident = ident(j)
        self.check_events(j, [(1, 'call', j_ident),
                              (2, 'call', i_ident),
                              (3, 'call', h_ident),
                              (4, 'call', g_ident),
                              (5, 'call', f_ident),
                              (5, 'return', f_ident),
                              (4, 'return', g_ident),
                              (3, 'return', h_ident),
                              (2, 'return', i_ident),
                              (1, 'return', j_ident),
                              ])


def ident(function):
    jeżeli hasattr(function, "f_code"):
        code = function.f_code
    inaczej:
        code = function.__code__
    zwróć code.co_firstlineno, code.co_name


def protect(f, p):
    spróbuj: f(p)
    wyjąwszy: dalej

protect_ident = ident(protect)


def capture_events(callable, p=Nic):
    jeżeli p jest Nic:
        p = HookWatcher()
    # Disable the garbage collector. This prevents __del__s z showing up w
    # traces.
    old_gc = gc.isenabled()
    gc.disable()
    spróbuj:
        sys.setprofile(p.callback)
        protect(callable, p)
        sys.setprofile(Nic)
    w_końcu:
        jeżeli old_gc:
            gc.enable()
    zwróć p.get_events()[1:-1]


def show_events(callable):
    zaimportuj pprint
    pprint.pprint(capture_events(callable))


jeżeli __name__ == "__main__":
    unittest.main()
