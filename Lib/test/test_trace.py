zaimportuj os
zaimportuj io
zaimportuj sys
z test.support zaimportuj TESTFN, rmtree, unlink, captured_stdout
zaimportuj unittest

zaimportuj trace
z trace zaimportuj CoverageResults, Trace

z test.tracedmodules zaimportuj testmod

#------------------------------- Utilities -----------------------------------#

def fix_ext_py(filename):
    """Given a .pyc filename converts it to the appropriate .py"""
    jeżeli filename.endswith('.pyc'):
        filename = filename[:-1]
    zwróć filename

def my_file_and_modname():
    """The .py file oraz module name of this file (__file__)"""
    modname = os.path.splitext(os.path.basename(__file__))[0]
    zwróć fix_ext_py(__file__), modname

def get_firstlineno(func):
    zwróć func.__code__.co_firstlineno

#-------------------- Target functions dla tracing ---------------------------#
#
# The relative line numbers of lines w these functions matter dla verifying
# tracing. Please modify the appropriate tests jeżeli you change one of the
# functions. Absolute line numbers don't matter.
#

def traced_func_linear(x, y):
    a = x
    b = y
    c = a + b
    zwróć c

def traced_func_loop(x, y):
    c = x
    dla i w range(5):
        c += y
    zwróć c

def traced_func_importing(x, y):
    zwróć x + y + testmod.func(1)

def traced_func_simple_caller(x):
    c = traced_func_linear(x, x)
    zwróć c + x

def traced_func_importing_caller(x):
    k = traced_func_simple_caller(x)
    k += traced_func_importing(k, x)
    zwróć k

def traced_func_generator(num):
    c = 5       # executed once
    dla i w range(num):
        uzyskaj i + c

def traced_func_calling_generator():
    k = 0
    dla i w traced_func_generator(10):
        k += i

def traced_doubler(num):
    zwróć num * 2

def traced_caller_list_comprehension():
    k = 10
    mylist = [traced_doubler(i) dla i w range(k)]
    zwróć mylist


klasa TracedClass(object):
    def __init__(self, x):
        self.a = x

    def inst_method_linear(self, y):
        zwróć self.a + y

    def inst_method_calling(self, x):
        c = self.inst_method_linear(x)
        zwróć c + traced_func_linear(x, c)

    @classmethod
    def class_method_linear(cls, y):
        zwróć y * 2

    @staticmethod
    def static_method_linear(y):
        zwróć y * 2


#------------------------------ Test cases -----------------------------------#


klasa TestLineCounts(unittest.TestCase):
    """White-box testing of line-counting, via runfunc"""
    def setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        self.tracer = Trace(count=1, trace=0, countfuncs=0, countcallers=0)
        self.my_py_filename = fix_ext_py(__file__)

    def test_traced_func_linear(self):
        result = self.tracer.runfunc(traced_func_linear, 2, 5)
        self.assertEqual(result, 7)

        # all lines are executed once
        expected = {}
        firstlineno = get_firstlineno(traced_func_linear)
        dla i w range(1, 5):
            expected[(self.my_py_filename, firstlineno +  i)] = 1

        self.assertEqual(self.tracer.results().counts, expected)

    def test_traced_func_loop(self):
        self.tracer.runfunc(traced_func_loop, 2, 3)

        firstlineno = get_firstlineno(traced_func_loop)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (self.my_py_filename, firstlineno + 2): 6,
            (self.my_py_filename, firstlineno + 3): 5,
            (self.my_py_filename, firstlineno + 4): 1,
        }
        self.assertEqual(self.tracer.results().counts, expected)

    def test_traced_func_importing(self):
        self.tracer.runfunc(traced_func_importing, 2, 5)

        firstlineno = get_firstlineno(traced_func_importing)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (fix_ext_py(testmod.__file__), 2): 1,
            (fix_ext_py(testmod.__file__), 3): 1,
        }

        self.assertEqual(self.tracer.results().counts, expected)

    def test_trace_func_generator(self):
        self.tracer.runfunc(traced_func_calling_generator)

        firstlineno_calling = get_firstlineno(traced_func_calling_generator)
        firstlineno_gen = get_firstlineno(traced_func_generator)
        expected = {
            (self.my_py_filename, firstlineno_calling + 1): 1,
            (self.my_py_filename, firstlineno_calling + 2): 11,
            (self.my_py_filename, firstlineno_calling + 3): 10,
            (self.my_py_filename, firstlineno_gen + 1): 1,
            (self.my_py_filename, firstlineno_gen + 2): 11,
            (self.my_py_filename, firstlineno_gen + 3): 10,
        }
        self.assertEqual(self.tracer.results().counts, expected)

    def test_trace_list_comprehension(self):
        self.tracer.runfunc(traced_caller_list_comprehension)

        firstlineno_calling = get_firstlineno(traced_caller_list_comprehension)
        firstlineno_called = get_firstlineno(traced_doubler)
        expected = {
            (self.my_py_filename, firstlineno_calling + 1): 1,
            # List compehentions work differently w 3.x, so the count
            # below changed compared to 2.x.
            (self.my_py_filename, firstlineno_calling + 2): 12,
            (self.my_py_filename, firstlineno_calling + 3): 1,
            (self.my_py_filename, firstlineno_called + 1): 10,
        }
        self.assertEqual(self.tracer.results().counts, expected)


    def test_linear_methods(self):
        # XXX todo: later add 'static_method_linear' oraz 'class_method_linear'
        # here, once issue1764286 jest resolved
        #
        dla methname w ['inst_method_linear',]:
            tracer = Trace(count=1, trace=0, countfuncs=0, countcallers=0)
            traced_obj = TracedClass(25)
            method = getattr(traced_obj, methname)
            tracer.runfunc(method, 20)

            firstlineno = get_firstlineno(method)
            expected = {
                (self.my_py_filename, firstlineno + 1): 1,
            }
            self.assertEqual(tracer.results().counts, expected)

klasa TestRunExecCounts(unittest.TestCase):
    """A simple sanity test of line-counting, via runctx (exec)"""
    def setUp(self):
        self.my_py_filename = fix_ext_py(__file__)
        self.addCleanup(sys.settrace, sys.gettrace())

    def test_exec_counts(self):
        self.tracer = Trace(count=1, trace=0, countfuncs=0, countcallers=0)
        code = r'''traced_func_loop(2, 5)'''
        code = compile(code, __file__, 'exec')
        self.tracer.runctx(code, globals(), vars())

        firstlineno = get_firstlineno(traced_func_loop)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (self.my_py_filename, firstlineno + 2): 6,
            (self.my_py_filename, firstlineno + 3): 5,
            (self.my_py_filename, firstlineno + 4): 1,
        }

        # When used through 'run', some other spurious counts are produced, like
        # the settrace of threading, which we ignore, just making sure that the
        # counts fo traced_func_loop were right.
        #
        dla k w expected.keys():
            self.assertEqual(self.tracer.results().counts[k], expected[k])


klasa TestFuncs(unittest.TestCase):
    """White-box testing of funcs tracing"""
    def setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        self.tracer = Trace(count=0, trace=0, countfuncs=1)
        self.filemod = my_file_and_modname()
        self._saved_tracefunc = sys.gettrace()

    def tearDown(self):
        jeżeli self._saved_tracefunc jest nie Nic:
            sys.settrace(self._saved_tracefunc)

    def test_simple_caller(self):
        self.tracer.runfunc(traced_func_simple_caller, 1)

        expected = {
            self.filemod + ('traced_func_simple_caller',): 1,
            self.filemod + ('traced_func_linear',): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)

    def test_loop_caller_importing(self):
        self.tracer.runfunc(traced_func_importing_caller, 1)

        expected = {
            self.filemod + ('traced_func_simple_caller',): 1,
            self.filemod + ('traced_func_linear',): 1,
            self.filemod + ('traced_func_importing_caller',): 1,
            self.filemod + ('traced_func_importing',): 1,
            (fix_ext_py(testmod.__file__), 'testmod', 'func'): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)

    @unittest.skipIf(hasattr(sys, 'gettrace') oraz sys.gettrace(),
                     'pre-existing trace function throws off measurements')
    def test_inst_method_calling(self):
        obj = TracedClass(20)
        self.tracer.runfunc(obj.inst_method_calling, 1)

        expected = {
            self.filemod + ('TracedClass.inst_method_calling',): 1,
            self.filemod + ('TracedClass.inst_method_linear',): 1,
            self.filemod + ('traced_func_linear',): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)


klasa TestCallers(unittest.TestCase):
    """White-box testing of callers tracing"""
    def setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        self.tracer = Trace(count=0, trace=0, countcallers=1)
        self.filemod = my_file_and_modname()

    @unittest.skipIf(hasattr(sys, 'gettrace') oraz sys.gettrace(),
                     'pre-existing trace function throws off measurements')
    def test_loop_caller_importing(self):
        self.tracer.runfunc(traced_func_importing_caller, 1)

        expected = {
            ((os.path.splitext(trace.__file__)[0] + '.py', 'trace', 'Trace.runfunc'),
                (self.filemod + ('traced_func_importing_caller',))): 1,
            ((self.filemod + ('traced_func_simple_caller',)),
                (self.filemod + ('traced_func_linear',))): 1,
            ((self.filemod + ('traced_func_importing_caller',)),
                (self.filemod + ('traced_func_simple_caller',))): 1,
            ((self.filemod + ('traced_func_importing_caller',)),
                (self.filemod + ('traced_func_importing',))): 1,
            ((self.filemod + ('traced_func_importing',)),
                (fix_ext_py(testmod.__file__), 'testmod', 'func')): 1,
        }
        self.assertEqual(self.tracer.results().callers, expected)


# Created separately dla issue #3821
klasa TestCoverage(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())

    def tearDown(self):
        rmtree(TESTFN)
        unlink(TESTFN)

    def _coverage(self, tracer,
                  cmd='zaimportuj test.support, test.test_pprint;'
                      'test.support.run_unittest(test.test_pprint.QueryTestCase)'):
        tracer.run(cmd)
        r = tracer.results()
        r.write_results(show_missing=Prawda, summary=Prawda, coverdir=TESTFN)

    def test_coverage(self):
        tracer = trace.Trace(trace=0, count=1)
        przy captured_stdout() jako stdout:
            self._coverage(tracer)
        stdout = stdout.getvalue()
        self.assertPrawda("pprint.py" w stdout)
        self.assertPrawda("case.py" w stdout)   # z unittest
        files = os.listdir(TESTFN)
        self.assertPrawda("pprint.cover" w files)
        self.assertPrawda("unittest.case.cover" w files)

    def test_coverage_ignore(self):
        # Ignore all files, nothing should be traced nor printed
        libpath = os.path.normpath(os.path.dirname(os.__file__))
        # sys.prefix does nie work when running z a checkout
        tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,
                             libpath], trace=0, count=1)
        przy captured_stdout() jako stdout:
            self._coverage(tracer)
        jeżeli os.path.exists(TESTFN):
            files = os.listdir(TESTFN)
            self.assertEqual(files, ['_importlib.cover'])  # Ignore __import__

    def test_issue9936(self):
        tracer = trace.Trace(trace=0, count=1)
        modname = 'test.tracedmodules.testmod'
        # Ensure that the module jest executed w import
        jeżeli modname w sys.modules:
            usuń sys.modules[modname]
        cmd = ("zaimportuj test.tracedmodules.testmod jako t;"
               "t.func(0); t.func2();")
        przy captured_stdout() jako stdout:
            self._coverage(tracer, cmd)
        stdout.seek(0)
        stdout.readline()
        coverage = {}
        dla line w stdout:
            lines, cov, module = line.split()[:3]
            coverage[module] = (int(lines), int(cov[:-1]))
        # XXX This jest needed to run regrtest.py jako a script
        modname = trace._fullmodname(sys.modules[modname].__file__)
        self.assertIn(modname, coverage)
        self.assertEqual(coverage[modname], (5, 100))

### Tests that don't mess przy sys.settrace oraz can be traced
### themselves TODO: Skip tests that do mess przy sys.settrace when
### regrtest jest invoked przy -T option.
klasa Test_Ignore(unittest.TestCase):
    def test_ignored(self):
        jn = os.path.join
        ignore = trace._Ignore(['x', 'y.z'], [jn('foo', 'bar')])
        self.assertPrawda(ignore.names('x.py', 'x'))
        self.assertNieprawda(ignore.names('xy.py', 'xy'))
        self.assertNieprawda(ignore.names('y.py', 'y'))
        self.assertPrawda(ignore.names(jn('foo', 'bar', 'baz.py'), 'baz'))
        self.assertNieprawda(ignore.names(jn('bar', 'z.py'), 'z'))
        # Matched before.
        self.assertPrawda(ignore.names(jn('bar', 'baz.py'), 'baz'))


klasa TestDeprecatedMethods(unittest.TestCase):

    def test_deprecated_usage(self):
        sio = io.StringIO()
        przy self.assertWarns(DeprecationWarning):
            trace.usage(sio)
        self.assertIn('Usage:', sio.getvalue())

    def test_deprecated_Ignore(self):
        przy self.assertWarns(DeprecationWarning):
            trace.Ignore()

    def test_deprecated_modname(self):
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual("spam", trace.modname("spam"))

    def test_deprecated_fullmodname(self):
        przy self.assertWarns(DeprecationWarning):
            self.assertEqual("spam", trace.fullmodname("spam"))

    def test_deprecated_find_lines_from_code(self):
        przy self.assertWarns(DeprecationWarning):
            def foo():
                dalej
            trace.find_lines_from_code(foo.__code__, ["eggs"])

    def test_deprecated_find_lines(self):
        przy self.assertWarns(DeprecationWarning):
            def foo():
                dalej
            trace.find_lines(foo.__code__, ["eggs"])

    def test_deprecated_find_strings(self):
        przy open(TESTFN, 'w') jako fd:
            self.addCleanup(unlink, TESTFN)
        przy self.assertWarns(DeprecationWarning):
            trace.find_strings(fd.name)

    def test_deprecated_find_executable_linenos(self):
        przy open(TESTFN, 'w') jako fd:
            self.addCleanup(unlink, TESTFN)
        przy self.assertWarns(DeprecationWarning):
            trace.find_executable_linenos(fd.name)


jeżeli __name__ == '__main__':
    unittest.main()
