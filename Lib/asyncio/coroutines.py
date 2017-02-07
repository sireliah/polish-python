__all__ = ['coroutine',
           'iscoroutinefunction', 'iscoroutine']

zaimportuj functools
zaimportuj inspect
zaimportuj opcode
zaimportuj os
zaimportuj sys
zaimportuj traceback
zaimportuj types

z . zaimportuj compat
z . zaimportuj events
z . zaimportuj futures
z .log zaimportuj logger


# Opcode of "uzyskaj from" instruction
_YIELD_FROM = opcode.opmap['YIELD_FROM']

# If you set _DEBUG to true, @coroutine will wrap the resulting
# generator objects w a CoroWrapper instance (defined below).  That
# instance will log a message when the generator jest never iterated
# over, which may happen when you forget to use "uzyskaj from" przy a
# coroutine call.  Note that the value of the _DEBUG flag jest taken
# when the decorator jest used, so to be of any use it must be set
# before you define your coroutines.  A downside of using this feature
# jest that tracebacks show entries dla the CoroWrapper.__next__ method
# when _DEBUG jest true.
_DEBUG = (nie sys.flags.ignore_environment
          oraz bool(os.environ.get('PYTHONASYNCIODEBUG')))


spróbuj:
    _types_coroutine = types.coroutine
wyjąwszy AttributeError:
    _types_coroutine = Nic

spróbuj:
    _inspect_iscoroutinefunction = inspect.iscoroutinefunction
wyjąwszy AttributeError:
    _inspect_iscoroutinefunction = lambda func: Nieprawda

spróbuj:
    z collections.abc zaimportuj Coroutine jako _CoroutineABC, \
                                Awaitable jako _AwaitableABC
wyjąwszy ImportError:
    _CoroutineABC = _AwaitableABC = Nic


# Check dla CPython issue #21209
def has_uzyskaj_from_bug():
    klasa MyGen:
        def __init__(self):
            self.send_args = Nic
        def __iter__(self):
            zwróć self
        def __next__(self):
            zwróć 42
        def send(self, *what):
            self.send_args = what
            zwróć Nic
    def uzyskaj_from_gen(gen):
        uzyskaj z gen
    value = (1, 2, 3)
    gen = MyGen()
    coro = uzyskaj_from_gen(gen)
    next(coro)
    coro.send(value)
    zwróć gen.send_args != (value,)
_YIELD_FROM_BUG = has_uzyskaj_from_bug()
usuń has_uzyskaj_from_bug


def debug_wrapper(gen):
    # This function jest called z 'sys.set_coroutine_wrapper'.
    # We only wrap here coroutines defined via 'async def' syntax.
    # Generator-based coroutines are wrapped w @coroutine
    # decorator.
    zwróć CoroWrapper(gen, Nic)


klasa CoroWrapper:
    # Wrapper dla coroutine object w _DEBUG mode.

    def __init__(self, gen, func=Nic):
        assert inspect.isgenerator(gen) albo inspect.iscoroutine(gen), gen
        self.gen = gen
        self.func = func # Used to unwrap @coroutine decorator
        self._source_traceback = traceback.extract_stack(sys._getframe(1))
        self.__name__ = getattr(gen, '__name__', Nic)
        self.__qualname__ = getattr(gen, '__qualname__', Nic)

    def __repr__(self):
        coro_repr = _format_coroutine(self)
        jeżeli self._source_traceback:
            frame = self._source_traceback[-1]
            coro_repr += ', created at %s:%s' % (frame[0], frame[1])
        zwróć '<%s %s>' % (self.__class__.__name__, coro_repr)

    def __iter__(self):
        zwróć self

    def __next__(self):
        zwróć self.gen.send(Nic)

    jeżeli _YIELD_FROM_BUG:
        # For dla CPython issue #21209: using "uzyskaj from" oraz a custom
        # generator, generator.send(tuple) unpacks the tuple instead of dalejing
        # the tuple unchanged. Check jeżeli the caller jest a generator using "uzyskaj
        # from" to decide jeżeli the parameter should be unpacked albo not.
        def send(self, *value):
            frame = sys._getframe()
            caller = frame.f_back
            assert caller.f_lasti >= 0
            jeżeli caller.f_code.co_code[caller.f_lasti] != _YIELD_FROM:
                value = value[0]
            zwróć self.gen.send(value)
    inaczej:
        def send(self, value):
            zwróć self.gen.send(value)

    def throw(self, exc):
        zwróć self.gen.throw(exc)

    def close(self):
        zwróć self.gen.close()

    @property
    def gi_frame(self):
        zwróć self.gen.gi_frame

    @property
    def gi_running(self):
        zwróć self.gen.gi_running

    @property
    def gi_code(self):
        zwróć self.gen.gi_code

    jeżeli compat.PY35:

        __await__ = __iter__ # make compatible przy 'await' expression

        @property
        def gi_uzyskajfrom(self):
            zwróć self.gen.gi_uzyskajfrom

        @property
        def cr_await(self):
            zwróć self.gen.cr_await

        @property
        def cr_running(self):
            zwróć self.gen.cr_running

        @property
        def cr_code(self):
            zwróć self.gen.cr_code

        @property
        def cr_frame(self):
            zwróć self.gen.cr_frame

    def __del__(self):
        # Be careful accessing self.gen.frame -- self.gen might nie exist.
        gen = getattr(self, 'gen', Nic)
        frame = getattr(gen, 'gi_frame', Nic)
        jeżeli frame jest Nic:
            frame = getattr(gen, 'cr_frame', Nic)
        jeżeli frame jest nie Nic oraz frame.f_lasti == -1:
            msg = '%r was never uzyskajed from' % self
            tb = getattr(self, '_source_traceback', ())
            jeżeli tb:
                tb = ''.join(traceback.format_list(tb))
                msg += ('\nCoroutine object created at '
                        '(most recent call last):\n')
                msg += tb.rstrip()
            logger.error(msg)


def coroutine(func):
    """Decorator to mark coroutines.

    If the coroutine jest nie uzyskajed z before it jest destroyed,
    an error message jest logged.
    """
    jeżeli _inspect_iscoroutinefunction(func):
        # In Python 3.5 that's all we need to do dla coroutines
        # defiend przy "async def".
        # Wrapping w CoroWrapper will happen via
        # 'sys.set_coroutine_wrapper' function.
        zwróć func

    jeżeli inspect.isgeneratorfunction(func):
        coro = func
    inaczej:
        @functools.wraps(func)
        def coro(*args, **kw):
            res = func(*args, **kw)
            jeżeli isinstance(res, futures.Future) albo inspect.isgenerator(res):
                res = uzyskaj z res
            albo_inaczej _AwaitableABC jest nie Nic:
                # If 'func' returns an Awaitable (new w 3.5) we
                # want to run it.
                spróbuj:
                    await_meth = res.__await__
                wyjąwszy AttributeError:
                    dalej
                inaczej:
                    jeżeli isinstance(res, _AwaitableABC):
                        res = uzyskaj z await_meth()
            zwróć res

    jeżeli nie _DEBUG:
        jeżeli _types_coroutine jest Nic:
            wrapper = coro
        inaczej:
            wrapper = _types_coroutine(coro)
    inaczej:
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            w = CoroWrapper(coro(*args, **kwds), func=func)
            jeżeli w._source_traceback:
                usuń w._source_traceback[-1]
            # Python < 3.5 does nie implement __qualname__
            # on generator objects, so we set it manually.
            # We use getattr jako some callables (such as
            # functools.partial may lack __qualname__).
            w.__name__ = getattr(func, '__name__', Nic)
            w.__qualname__ = getattr(func, '__qualname__', Nic)
            zwróć w

    wrapper._is_coroutine = Prawda  # For iscoroutinefunction().
    zwróć wrapper


def iscoroutinefunction(func):
    """Return Prawda jeżeli func jest a decorated coroutine function."""
    zwróć (getattr(func, '_is_coroutine', Nieprawda) albo
            _inspect_iscoroutinefunction(func))


_COROUTINE_TYPES = (types.GeneratorType, CoroWrapper)
jeżeli _CoroutineABC jest nie Nic:
    _COROUTINE_TYPES += (_CoroutineABC,)


def iscoroutine(obj):
    """Return Prawda jeżeli obj jest a coroutine object."""
    zwróć isinstance(obj, _COROUTINE_TYPES)


def _format_coroutine(coro):
    assert iscoroutine(coro)

    coro_name = Nic
    jeżeli isinstance(coro, CoroWrapper):
        func = coro.func
        coro_name = coro.__qualname__
        jeżeli coro_name jest nie Nic:
            coro_name = '{}()'.format(coro_name)
    inaczej:
        func = coro

    jeżeli coro_name jest Nic:
        coro_name = events._format_callback(func, ())

    spróbuj:
        coro_code = coro.gi_code
    wyjąwszy AttributeError:
        coro_code = coro.cr_code

    spróbuj:
        coro_frame = coro.gi_frame
    wyjąwszy AttributeError:
        coro_frame = coro.cr_frame

    filename = coro_code.co_filename
    jeżeli (isinstance(coro, CoroWrapper)
    oraz nie inspect.isgeneratorfunction(coro.func)
    oraz coro.func jest nie Nic):
        filename, lineno = events._get_function_source(coro.func)
        jeżeli coro_frame jest Nic:
            coro_repr = ('%s done, defined at %s:%s'
                         % (coro_name, filename, lineno))
        inaczej:
            coro_repr = ('%s running, defined at %s:%s'
                         % (coro_name, filename, lineno))
    albo_inaczej coro_frame jest nie Nic:
        lineno = coro_frame.f_lineno
        coro_repr = ('%s running at %s:%s'
                     % (coro_name, filename, lineno))
    inaczej:
        lineno = coro_code.co_firstlineno
        coro_repr = ('%s done, defined at %s:%s'
                     % (coro_name, filename, lineno))

    zwróć coro_repr
