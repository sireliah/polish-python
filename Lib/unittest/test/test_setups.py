zaimportuj io
zaimportuj sys

zaimportuj unittest


def resultFactory(*_):
    zwróć unittest.TestResult()


klasa TestSetups(unittest.TestCase):

    def getRunner(self):
        zwróć unittest.TextTestRunner(resultclass=resultFactory,
                                          stream=io.StringIO())
    def runTests(self, *cases):
        suite = unittest.TestSuite()
        dla case w cases:
            tests = unittest.defaultTestLoader.loadTestsFromTestCase(case)
            suite.addTests(tests)

        runner = self.getRunner()

        # creating a nested suite exposes some potential bugs
        realSuite = unittest.TestSuite()
        realSuite.addTest(suite)
        # adding empty suites to the end exposes potential bugs
        suite.addTest(unittest.TestSuite())
        realSuite.addTest(unittest.TestSuite())
        zwróć runner.run(realSuite)

    def test_setup_class(self):
        klasa Test(unittest.TestCase):
            setUpCalled = 0
            @classmethod
            def setUpClass(cls):
                Test.setUpCalled += 1
                unittest.TestCase.setUpClass()
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        result = self.runTests(Test)

        self.assertEqual(Test.setUpCalled, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    def test_teardown_class(self):
        klasa Test(unittest.TestCase):
            tearDownCalled = 0
            @classmethod
            def tearDownClass(cls):
                Test.tearDownCalled += 1
                unittest.TestCase.tearDownClass()
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        result = self.runTests(Test)

        self.assertEqual(Test.tearDownCalled, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    def test_teardown_class_two_classes(self):
        klasa Test(unittest.TestCase):
            tearDownCalled = 0
            @classmethod
            def tearDownClass(cls):
                Test.tearDownCalled += 1
                unittest.TestCase.tearDownClass()
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        klasa Test2(unittest.TestCase):
            tearDownCalled = 0
            @classmethod
            def tearDownClass(cls):
                Test2.tearDownCalled += 1
                unittest.TestCase.tearDownClass()
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        result = self.runTests(Test, Test2)

        self.assertEqual(Test.tearDownCalled, 1)
        self.assertEqual(Test2.tearDownCalled, 1)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(len(result.errors), 0)

    def test_error_in_setupclass(self):
        klasa BrokenTest(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                podnieś TypeError('foo')
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        result = self.runTests(BrokenTest)

        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 1)
        error, _ = result.errors[0]
        self.assertEqual(str(error),
                    'setUpClass (%s.%s)' % (__name__, BrokenTest.__qualname__))

    def test_error_in_teardown_class(self):
        klasa Test(unittest.TestCase):
            tornDown = 0
            @classmethod
            def tearDownClass(cls):
                Test.tornDown += 1
                podnieś TypeError('foo')
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        klasa Test2(unittest.TestCase):
            tornDown = 0
            @classmethod
            def tearDownClass(cls):
                Test2.tornDown += 1
                podnieś TypeError('foo')
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        result = self.runTests(Test, Test2)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(Test.tornDown, 1)
        self.assertEqual(Test2.tornDown, 1)

        error, _ = result.errors[0]
        self.assertEqual(str(error),
                    'tearDownClass (%s.%s)' % (__name__, Test.__qualname__))

    def test_class_not_torndown_when_setup_fails(self):
        klasa Test(unittest.TestCase):
            tornDown = Nieprawda
            @classmethod
            def setUpClass(cls):
                podnieś TypeError
            @classmethod
            def tearDownClass(cls):
                Test.tornDown = Prawda
                podnieś TypeError('foo')
            def test_one(self):
                dalej

        self.runTests(Test)
        self.assertNieprawda(Test.tornDown)

    def test_class_not_setup_or_torndown_when_skipped(self):
        klasa Test(unittest.TestCase):
            classSetUp = Nieprawda
            tornDown = Nieprawda
            @classmethod
            def setUpClass(cls):
                Test.classSetUp = Prawda
            @classmethod
            def tearDownClass(cls):
                Test.tornDown = Prawda
            def test_one(self):
                dalej

        Test = unittest.skip("hop")(Test)
        self.runTests(Test)
        self.assertNieprawda(Test.classSetUp)
        self.assertNieprawda(Test.tornDown)

    def test_setup_teardown_order_with_pathological_suite(self):
        results = []

        klasa Module1(object):
            @staticmethod
            def setUpModule():
                results.append('Module1.setUpModule')
            @staticmethod
            def tearDownModule():
                results.append('Module1.tearDownModule')

        klasa Module2(object):
            @staticmethod
            def setUpModule():
                results.append('Module2.setUpModule')
            @staticmethod
            def tearDownModule():
                results.append('Module2.tearDownModule')

        klasa Test1(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                results.append('setup 1')
            @classmethod
            def tearDownClass(cls):
                results.append('teardown 1')
            def testOne(self):
                results.append('Test1.testOne')
            def testTwo(self):
                results.append('Test1.testTwo')

        klasa Test2(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                results.append('setup 2')
            @classmethod
            def tearDownClass(cls):
                results.append('teardown 2')
            def testOne(self):
                results.append('Test2.testOne')
            def testTwo(self):
                results.append('Test2.testTwo')

        klasa Test3(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                results.append('setup 3')
            @classmethod
            def tearDownClass(cls):
                results.append('teardown 3')
            def testOne(self):
                results.append('Test3.testOne')
            def testTwo(self):
                results.append('Test3.testTwo')

        Test1.__module__ = Test2.__module__ = 'Module'
        Test3.__module__ = 'Module2'
        sys.modules['Module'] = Module1
        sys.modules['Module2'] = Module2

        first = unittest.TestSuite((Test1('testOne'),))
        second = unittest.TestSuite((Test1('testTwo'),))
        third = unittest.TestSuite((Test2('testOne'),))
        fourth = unittest.TestSuite((Test2('testTwo'),))
        fifth = unittest.TestSuite((Test3('testOne'),))
        sixth = unittest.TestSuite((Test3('testTwo'),))
        suite = unittest.TestSuite((first, second, third, fourth, fifth, sixth))

        runner = self.getRunner()
        result = runner.run(suite)
        self.assertEqual(result.testsRun, 6)
        self.assertEqual(len(result.errors), 0)

        self.assertEqual(results,
                         ['Module1.setUpModule', 'setup 1',
                          'Test1.testOne', 'Test1.testTwo', 'teardown 1',
                          'setup 2', 'Test2.testOne', 'Test2.testTwo',
                          'teardown 2', 'Module1.tearDownModule',
                          'Module2.setUpModule', 'setup 3',
                          'Test3.testOne', 'Test3.testTwo',
                          'teardown 3', 'Module2.tearDownModule'])

    def test_setup_module(self):
        klasa Module(object):
            moduleSetup = 0
            @staticmethod
            def setUpModule():
                Module.moduleSetup += 1

        klasa Test(unittest.TestCase):
            def test_one(self):
                dalej
            def test_two(self):
                dalej
        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test)
        self.assertEqual(Module.moduleSetup, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    def test_error_in_setup_module(self):
        klasa Module(object):
            moduleSetup = 0
            moduleTornDown = 0
            @staticmethod
            def setUpModule():
                Module.moduleSetup += 1
                podnieś TypeError('foo')
            @staticmethod
            def tearDownModule():
                Module.moduleTornDown += 1

        klasa Test(unittest.TestCase):
            classSetUp = Nieprawda
            classTornDown = Nieprawda
            @classmethod
            def setUpClass(cls):
                Test.classSetUp = Prawda
            @classmethod
            def tearDownClass(cls):
                Test.classTornDown = Prawda
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        klasa Test2(unittest.TestCase):
            def test_one(self):
                dalej
            def test_two(self):
                dalej
        Test.__module__ = 'Module'
        Test2.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test, Test2)
        self.assertEqual(Module.moduleSetup, 1)
        self.assertEqual(Module.moduleTornDown, 0)
        self.assertEqual(result.testsRun, 0)
        self.assertNieprawda(Test.classSetUp)
        self.assertNieprawda(Test.classTornDown)
        self.assertEqual(len(result.errors), 1)
        error, _ = result.errors[0]
        self.assertEqual(str(error), 'setUpModule (Module)')

    def test_testcase_with_missing_module(self):
        klasa Test(unittest.TestCase):
            def test_one(self):
                dalej
            def test_two(self):
                dalej
        Test.__module__ = 'Module'
        sys.modules.pop('Module', Nic)

        result = self.runTests(Test)
        self.assertEqual(result.testsRun, 2)

    def test_teardown_module(self):
        klasa Module(object):
            moduleTornDown = 0
            @staticmethod
            def tearDownModule():
                Module.moduleTornDown += 1

        klasa Test(unittest.TestCase):
            def test_one(self):
                dalej
            def test_two(self):
                dalej
        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test)
        self.assertEqual(Module.moduleTornDown, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    def test_error_in_teardown_module(self):
        klasa Module(object):
            moduleTornDown = 0
            @staticmethod
            def tearDownModule():
                Module.moduleTornDown += 1
                podnieś TypeError('foo')

        klasa Test(unittest.TestCase):
            classSetUp = Nieprawda
            classTornDown = Nieprawda
            @classmethod
            def setUpClass(cls):
                Test.classSetUp = Prawda
            @classmethod
            def tearDownClass(cls):
                Test.classTornDown = Prawda
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        klasa Test2(unittest.TestCase):
            def test_one(self):
                dalej
            def test_two(self):
                dalej
        Test.__module__ = 'Module'
        Test2.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test, Test2)
        self.assertEqual(Module.moduleTornDown, 1)
        self.assertEqual(result.testsRun, 4)
        self.assertPrawda(Test.classSetUp)
        self.assertPrawda(Test.classTornDown)
        self.assertEqual(len(result.errors), 1)
        error, _ = result.errors[0]
        self.assertEqual(str(error), 'tearDownModule (Module)')

    def test_skiptest_in_setupclass(self):
        klasa Test(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                podnieś unittest.SkipTest('foo')
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        result = self.runTests(Test)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.skipped), 1)
        skipped = result.skipped[0][0]
        self.assertEqual(str(skipped),
                    'setUpClass (%s.%s)' % (__name__, Test.__qualname__))

    def test_skiptest_in_setupmodule(self):
        klasa Test(unittest.TestCase):
            def test_one(self):
                dalej
            def test_two(self):
                dalej

        klasa Module(object):
            @staticmethod
            def setUpModule():
                podnieś unittest.SkipTest('foo')

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.skipped), 1)
        skipped = result.skipped[0][0]
        self.assertEqual(str(skipped), 'setUpModule (Module)')

    def test_suite_debug_executes_setups_and_teardowns(self):
        ordering = []

        klasa Module(object):
            @staticmethod
            def setUpModule():
                ordering.append('setUpModule')
            @staticmethod
            def tearDownModule():
                ordering.append('tearDownModule')

        klasa Test(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                ordering.append('setUpClass')
            @classmethod
            def tearDownClass(cls):
                ordering.append('tearDownClass')
            def test_something(self):
                ordering.append('test_something')

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
        suite.debug()
        expectedOrder = ['setUpModule', 'setUpClass', 'test_something', 'tearDownClass', 'tearDownModule']
        self.assertEqual(ordering, expectedOrder)

    def test_suite_debug_propagates_exceptions(self):
        klasa Module(object):
            @staticmethod
            def setUpModule():
                jeżeli phase == 0:
                    podnieś Exception('setUpModule')
            @staticmethod
            def tearDownModule():
                jeżeli phase == 1:
                    podnieś Exception('tearDownModule')

        klasa Test(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                jeżeli phase == 2:
                    podnieś Exception('setUpClass')
            @classmethod
            def tearDownClass(cls):
                jeżeli phase == 3:
                    podnieś Exception('tearDownClass')
            def test_something(self):
                jeżeli phase == 4:
                    podnieś Exception('test_something')

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        messages = ('setUpModule', 'tearDownModule', 'setUpClass', 'tearDownClass', 'test_something')
        dla phase, msg w enumerate(messages):
            _suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
            suite = unittest.TestSuite([_suite])
            przy self.assertRaisesRegex(Exception, msg):
                suite.debug()


jeżeli __name__ == '__main__':
    unittest.main()
